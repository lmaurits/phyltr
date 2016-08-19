"""Usage:
    phyltr height [<files>]

Print the heights of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import dendropy

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    # Read trees
    for line in fileinput.input():
        t = dendropy.Tree.get_from_string(line,schema="newick")
        print(t.seed_node.distance_from_tip())

    return 0
