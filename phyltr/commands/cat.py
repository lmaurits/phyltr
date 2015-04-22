import fileinput
import optparse
import sys

import ete2

def run():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option("-o", "--output", action="store", dest="filename",
        help="save clades to FILE", metavar="FILE")
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args()
    if not files:
        files = ["-"]

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

            # Attempt to parse the first whitespace-separated chunk on the line
            # which starts with an opening bracket.  Fail silently.
            chunks = line.split()
            for chunk in chunks:
                if chunk.startswith("("):
                    if chunk.count("(") == chunk.count(")"):
                        # Smells like a tree!
                        tree_strings.append(chunk)
                        break

        burnin = int(round((options.burnin/100.0)*len(tree_strings)))
        tree_strings = tree_strings[burnin::options.subsample]

        for tree_string in tree_strings:
           try:
               t = ete2.Tree(tree_string)
           except ete2.parser.newick.NewickError:
               continue
           if isNexus and nexus_trans:
               for node in t.traverse():
                   if node.name != "NoName" and node.name in nexus_trans:
                       node.name = nexus_trans[node.name]
           print t.write()

    # Done
    return 0
