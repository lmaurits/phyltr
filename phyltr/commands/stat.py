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

import ete2

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
    # Read trees
    for line in fileinput.input():
        t = ete2.Tree(line)
        cache = t.get_cached_content()
        tree_leaves = cache[t]
        tree_count += 1
        if firsttree:
            taxa_count = len(tree_leaves)
            taxa_names = [l.name for l in tree_leaves]
            topologically_unique_trees.append(t)
            leave_ages = [t.get_distance(l) for l in tree_leaves]
            if abs(max(leave_ages) - min(leave_ages)) < max(leave_ages)/1000.0:
                ultrametric = True
            firsttree = False
        tree_ages.append(t.get_farthest_leaf()[1])
        unique = True
        for u in topologically_unique_trees:
            if u.robinson_foulds(t)[0] == 0.0:
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
