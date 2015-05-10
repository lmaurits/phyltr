"""Usage:
    phyltr delete taxa [<files>]

Delete a specified set of leaf nodes from a treestream.

OPTIONS:

    taxa
        A comma-separated list of leaf taxon names

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

    first = True
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        if first:
            leaves = [l.name for l in t.get_leaves()]
            survivors = set(leaves) - targets
            first = False
        t.prune(survivors)
        print t.write()

    # Done
    return 0
