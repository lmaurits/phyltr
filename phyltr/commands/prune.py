"""Usage:
    phyltr prune taxa [<options>] [<files>]

Delete a specified set of nodes from the tree.

OPTIONS:

    taxa
        A comma-separated list of leaf taxon to delete from the tree

    -i, --inverse
        Specify an "inverse prune": delete all taxa *except* those given in
        the taxa option.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import sys

import ete2

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-i', '--inverse', action="store_true", default=False, dest="inverse")
    parser.add_option('-v', '--value', default=None)
    options, files = parser.parse_args()

    if options.attribute and options.value:
        by_attribute = True
    elif options.filename:
        fp = open(options.filename, "r")
        taxa = [t.strip() for t in fp.readlines()]
        by_attribute = False
    elif files:
        taxa = set(files[0].split(","))
        files = files[1:]
        by_attribute = False
    else:
        # Improper usage
        sys.stderr.write("Must specify either a list of taxa, a file of taxa, or an attribute and value.\n")
        sys.exit(1)

    first = True
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        # Decide which leaves to prune
        if by_attribute:
            if options.inverse:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,options.attribute) and getattr(l,options.attribute) == options.value]
            else:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,options.attribute) and getattr(l,options.attribute) != options.value]
        else:
            if options.inverse:
                pruning_taxa = [l for l in t.get_leaves() if l.name in taxa]
            else:
                pruning_taxa = [l for l in t.get_leaves() if l.name not in taxa]
        # Do the deed
        t.prune(pruning_taxa)
        print t.write(features=[],format_root_node=True)

    # Done
    return 0
