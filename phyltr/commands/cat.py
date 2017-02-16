"""Usage:
    phyltr cat [<options>] [<files>]

Extract phylogenetic trees from the specified files and print them as a treestream.  The trees may contain trees formatted as a phyltr treestream or a NEXUS file.

OPTIONS:

    -b, --burnin
        Percentage of trees from each file to discard as "burnin".  Default is 0.
        
    -s, --subsample
        Frequency at which to subsample trees, i.e. "-s 10" will include
        only every 10th tree in the treestream.  Default is 1.
        
    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import re
import sys

import ete2

import phyltr.utils.phyoptparse as optparse

_BEAST_ANNOTATION_REGEX = "([a-zA-Z0-9_ \-]*?):(\[&.*?\])([0-9\.]+)([Ee])?(\-)?([0-9])*"
_BEAST_ANNOTATION_REGEX_2 = "([a-zA-Z0-9_ \-]*?)(\[&.*?\]):([0-9\.]+)([Ee])?(\-)?([0-9])*"
regex1 = re.compile(_BEAST_ANNOTATION_REGEX)
regex2 = re.compile(_BEAST_ANNOTATION_REGEX_2)

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)
    options, files = parser.parse_args()
    if not files:
        files = ["-"]

    # Read files
    for filename in files:
        if filename == "-":
            fp = sys.stdin
        else:
            fp = open(filename, "r")

        tree_strings = []
        firstline = True
        for line in fp:
            # Skip blank lines
            if not line:
                continue
            
            # Detect Nexus file format by checking first line
            if firstline:
                if line.strip() == "#NEXUS":
                    isNexus = True
                    inTranslate = False
                    nexus_trans = {}
                else:
                    isNexus = False
                firstline = False

            # Detect beginning of Nexus translate block
            if isNexus and "translate" in line.lower():
                inTranslate = True
                continue

            # Handle Nexus translate block
            if isNexus and inTranslate:
                # Detect ending of translate block...
                if line.strip() == ";":
                    inTranslate = False
                # ...or handle a line of translate block
                else:
                    if line.strip().endswith(";"):
                        line = line[:-1]
                        inTranslate = False
                    index, name = line.strip().split()
                    if name.endswith(","):
                        name = name[:-1]
                    nexus_trans[index] = name

            # Try to find a likely tree on this line and extract it
            if (
                    ")" in line and
                    ";" in line and
                    line.count("(") == line.count(")")
               ):
                # Smells like a tree!
                start = line.index("(")
                end = line.rindex(";") + 1
                tree_strings.append(line[start:end])

        burnin = int(round((options.burnin/100.0)*len(tree_strings)))
        tree_strings = tree_strings[burnin::options.subsample]

        while tree_strings:
            tree_string = tree_strings.pop(0)
            t = get_tree(tree_string)
            if not t:
                continue
            if isNexus and nexus_trans:
                for node in t.traverse():
                    if node.name and node.name in nexus_trans:
                        node.name = nexus_trans[node.name]
            if options.no_annotations:
                print t.write(format_root_node=True)
            else:
                print t.write(features=[],format_root_node=True)

    # Done
    return 0

def get_tree(tree_string):
    # FIXME
    # Make this much more elegant
    # Also, once a successful parse is achieved, remember the strategy and avoid brute force on subsequent trees

    # Do we need regex magic?
    if "[&" in tree_string and "&&NHX" not in tree_string:
        tree_string = regex1.sub(repl, tree_string)
        if "NHX" not in tree_string:
            tree_string = regex2.sub(repl, tree_string)

    # Try to parse tree as is
    try:
        t = ete2.Tree(tree_string)
        return t
    except (ValueError,ete2.parser.newick.NewickError):
        pass

    # Try to parse tree with internal node labels
    try:
        t = ete2.Tree(tree_string, format=1)
        return t
    except (ValueError,ete2.parser.newick.NewickError):
        # That didn't fix it.  Give up
        return None

def repl(m):
    name, annotation, dist = m.groups()[0:3]
    if len(m.groups()) > 3:
        # Exponential notation
        dist += "".join([str(x) for x in m.groups()[3:] if x])
    dist = float(dist)
    if annotation:
        bits = annotation[2:-1].split(",")
        # Handle BEAST's "vector annotations"
        # (comma-separated elements inside {}s)
        # by replacing the commas with pipes
        # (this approach subject to change?)
        newbits = []
        inside = False
        for bit in bits:
            if inside:
                newbits[-1] += "|" + bit
                if "}" in bit:
                    inside = False
            else:
                newbits.append(bit)
                if "{" in bit:
                    inside = True
        annotation = "[&&NHX:%s]" % ":".join(newbits)
    return "%s:%f%s" % (name, dist, annotation)

