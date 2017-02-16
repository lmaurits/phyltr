"""Usage:
    phyltr subtree taxa [<options>] [<files>]

Replace each tree with the minimal subtree containing the specified taxa.

OPTIONS:

    taxa
        A comma-separated list of leaf taxa to keep in the tree

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import ete2
import fileinput
import sys

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-v', '--value', default=None)
    options, files = parser.parse_args()

    if options.filename:
        fp = open(options.filename, "r")
        taxa = [t.strip() for t in fp.readlines()]
    elif not (options.attribute and options.value):
        if files:
            taxa = set(files[0].split(","))
            files = files[1:]
        else:
            # Improper usage
            sys.stderr.write("Must specify a list of taxa.\n")
            sys.exit(1)

    first = True
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        if options.attribute and options.value:
            mrca = list(t.get_monophyletic([options.value], options.attribute))[0]
            assert mrca != t
            t = mrca
        else:
            leaves = [l for l in t.get_leaves() if l.name in taxa]
            mrca = leaves[0].get_common_ancestor(leaves[1:])
            t = mrca
        print t.write(features=[],format_root_node=True)

    # Done
    return 0
