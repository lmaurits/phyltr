"""Usage:
    phyltr uniq [<options>] [<files>]

Merge all sets of trees with identical topologies in a tree stream into
single trees.  The branch lengths of the merged trees are computed from those
of all the trees with that topology.  Mean lengths are used by default.

OPTIONS:

    -l, --length
        Specifies the method used to compute branch lengths when trees with
        identical topologies are merged.  Must be one of: "max", "mean",
        "median", or "min".  Default is mean.
    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import itertools

import dendropy

from phyltr.utils.treestream_io import read_tree, write_tree
import phyltr.utils.cladeprob
import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-l', '--lengths', action="store", dest="lengths", default="mean")
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    topologies = {}
    tns = dendropy.TaxonNamespace()
    for line in fileinput.input(files):
        t = read_tree(t)
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        matched = False
        for exemplar in topologies:
            if dendropy.calculate.treecompare.symmetric_difference(t,exemplar) == 0:
                matched = True
                topologies[exemplar].append(t)
                break
        if not matched:
            topologies[t] = [t]
        
    for equ_class in topologies.values():
        for nodes in itertools.izip(*[t.seed_node.child_node_iter() for t in equ_class]):
            dists = [n.edge.length for n in nodes]
            if options.lengths == "max":
                dist = max(dists)
            elif options.lengths == "mean":
                dist = sum(dists) / len(dists)
            elif options.lengths == "median":
                dists.sort()
                l = len(dists)
                if l % 2 == 0:
                    dist = 0.5*(dists[l/2]+dists[l/2-1])
                else:
                    dist = dists[l/2]
            elif options.lengths == "min":
                dist = min(dists)
            nodes[0].edge.length = dist
        write_tree(equ_class[0])

    # Done
    return 0
