import fileinput
import optparse

import ete2

import phyltr.utils.cladeprob

def run():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-s', '--sort', action="store_true", dest="sort", default=False)
    parser.add_option("-o", "--output", action="store", dest="filename",
        help="save clades to FILE", metavar="FILE")
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    trees = []
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        trees.append(t)
        cp.add_tree(t)
    cp.compute_probabilities()

    # Save clade probabilities
    if options.filename:
        save_clades(cp, options.filename, options.frequency)

    # Annotate trees
    for t in trees:
        cp.annotate_tree(t)

    # Sort
    if options.sort:
        trees = [(cp.get_tree_prob(t),t) for t in trees]
        trees.sort()
        trees.reverse()
        trees = [t for (p,t) in trees]

    # Output
    for t in trees:
        print t.write()

    # Done
    return 0

def save_clades(cp, filename, threshold):
    clade_probs = [(cp.clade_probs[c], c) for c in cp.clade_probs]
    if threshold < 1.0:
        clade_probs = [(p, c) for (p, c) in clade_probs if p >= threshold]
    clade_probs.sort()
    clade_probs.reverse()

    fp = open(filename, "w")
    for p, c in clade_probs:
        fp.write("%f: [%s]\n" % (p, c))
    fp.close()
