"""Usage:
    phyltr prune taxa [<files>]

Delete a specified set of nodes from the tree.

OPTIONS:

    taxa
        A comma-separated list of leaf taxon to prune the tree down to

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
    parser.add_option('-t', '--taxa', action="store", dest="taxa")
    options, files = parser.parse_args()

    # Get set of targets
    if not options.taxa:
        targets = []
    else:
        targets = set(options.taxa.split(","))

    for line in fileinput.input(files):
        t = ete2.Tree(line)
        t.prune(targets)
        print t.write()

    # Done
    return 0
