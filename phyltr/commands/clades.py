import fileinput
import optparse

import ete2

import phyltr.utils.cladeprob

def run():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-s', '--sort', action="store_true", dest="sort", default=False)
    parser.add_option('-f', '--frequency', type="float", dest="threshold",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    trees = []
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        cp.add_tree(t)
    cp.compute_probabilities()

    # Prepare clade list
    clade_probs = [(cp.clade_probs[c], c) for c in cp.clade_probs]
    if options.threshold < 1.0:
        clade_probs = [(p, c) for (p, c) in clade_probs if p >= options.threshold]
    if options.sort:
        clade_probs.sort()
        clade_probs.reverse()

    # Output
    for p, c in clade_probs:
        print "%f: [%s]" % (p, c)

    # Done
    return 0
