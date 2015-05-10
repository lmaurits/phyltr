"""Usage:
    phyltr uniq [<files>]

Replace all sets of trees with identical topologies in a tree stream with
single trees, setting branch lengths to the mean of all the trees
instantiating that topology.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import itertools

import ete2

import phyltr.utils.cladeprob
import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
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
