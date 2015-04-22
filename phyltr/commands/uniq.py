import fileinput
import itertools
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
    topologies = {}
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        matched = False
        for exemplar in topologies:
            if t.robinson_foulds(exemplar)[0] == 0.0:
                matched = True
                topologies[exemplar].append(t)
                break
        if not matched:
            topologies[t] = [t]
        
    for equ_class in topologies.values():
        for nodes in itertools.izip(*[t.traverse() for t in equ_class]):
            dists = [n.dist for n in nodes]
            mean = sum(dists) / len(dists)
            nodes[0].dist = mean
        print equ_class[0].write()

    # Done
    return 0
