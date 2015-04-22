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

    for line in fileinput.input(files):
        t = ete2.Tree(line)
        t.prune(targets)
        print t.write()

    # Done
    return 0
