"""Usage:
    phyltr scale [<options>] [<files>]

Scale the branch lengths in a treestream by a constant factor.

OPTIONS:

    -s, --scale
        The factor to scale by, expressed in floating point notation.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import ete2

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-s', '--scale', type="float", default=1.0,
                help='Scaling factor.')
    options, files = parser.parse_args()

    # Read trees
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        # Scale branches
        for node in t.traverse():
            node.dist *= options.scale
        # Output
        print t.write()

    # Done
    return 0
