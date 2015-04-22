import fileinput
import optparse
import sys

import ete2

def run():

    # Parse options
    parser = optparse.OptionParser()
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
