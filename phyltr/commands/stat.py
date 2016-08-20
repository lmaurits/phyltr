"""Usage:
    phyltr stat [<files>]

Print basic properties of a tree stream, such as the number of trees and taxa.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import dendropy

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    # Go
    tree_count = 0
    taxa_count = 0
    ultrametric = False
    topologically_unique_trees = []
    tree_ages = []
    firsttree = True
    tns = dendropy.TaxonNamespace()
    # Read trees
    for line in fileinput.input():
        t = dendropy.Tree.get_from_string(line,schema="newick",rooting="default-rooted",taxon_namespace=tns)
        tree_leaves = t.leaf_nodes()
        tree_count += 1
        if firsttree:
            taxa_count = len(tree_leaves)
            taxa_names = [l.taxon.label for l in tree_leaves]
            topologically_unique_trees.append(t)
            leave_ages = [l.distance_from_root() for l in tree_leaves]
            if abs(max(leave_ages) - min(leave_ages)) < max(leave_ages)/1000.0:
                ultrametric = True
            firsttree = False
        tree_ages.append(max(leave_ages))
        unique = True
        for u in topologically_unique_trees:
            if dendropy.calculate.treecompare.symmetric_difference(t,u) == 0:
                unique = False
                break
        if unique:
            topologically_unique_trees.append(t)

    # Output
    print "Total taxa: %d" % taxa_count
    print "Total trees: %d" % tree_count
    print "Unique topologies: %d" % len(topologically_unique_trees)
    print "Are trees ultrametric? ", str(ultrametric)
    print "Mean tree age: %f" % (sum(tree_ages) / tree_count)

    # Done
    return 0
