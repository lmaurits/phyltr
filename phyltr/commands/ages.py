"""Usage:
    phyltr ages [<options>] taxa [<files>]

Print the age(s) of particular nodes in a treestream.  The nodes are either
leaf nodes, or the most recent common ancestor (MRCA) of a set of leaf nodes.
Ages are measured from the root of the tree.  If multiple taxa are provided
and the MRCA option is not enabled, the output will be a tab-separated list
of ages for the individual taxa.

OPTIONS:

    taxa
        A comma-separated list of leaf taxon names to print ages for

    -m, --mrca
        Output ages of the MRCA of the specified taxa

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
    parser.add_option('-m', '--mrca', action="store_true", dest="mrca", default=False)
    options, positional = parser.parse_args()
   
    taxa = positional[0].split(",")
    files = positional[1:] if len(positional) > 1 else []
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        if options.mrca:
            mrca = t.get_common_ancestor(taxa)
            print t.get_distance(mrca)
        else:
            taxa = [t.get_leaves_by_name(name=taxon)[0] for taxon in taxa]
            dists = [t.get_distance(n) for n in taxa]
            print "\t".join(map(str,dists))

    # Done
    return 0
