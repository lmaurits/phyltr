"""Usage:
    phyltr stat [<files>]

Print basic properties of a tree stream, such as the number of trees and taxa.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Stat(PhyltrCommand):

    def __init__(self):

        self.tree_count = 0
        self.taxa_count = 0
        self.ultrametric = False
        self.topologically_unique_trees = []
        self.tree_ages = []
        self.firsttree = True

    def process_tree(self, t):
        cache = t.get_cached_content()
        tree_leaves = cache[t]
        self.tree_count += 1
        if self.firsttree:
            self.taxa_count = len(tree_leaves)
            self.taxa_names = [l.name for l in tree_leaves]
            self.topologically_unique_trees.append(t)
            leave_ages = [t.get_distance(l) for l in tree_leaves]
            if abs(max(leave_ages) - min(leave_ages)) < max(leave_ages)/1000.0:
                self.ultrametric = True
            self.firsttree = False
        self.tree_ages.append(t.get_farthest_leaf()[1])
        unique = True
        for u in self.topologically_unique_trees:
            if u.robinson_foulds(t)[0] == 0.0:
                unique = False
                break
        if unique:
            self.topologically_unique_trees.append(t)
        return None

    def postprocess(self):
        print "Total taxa: %d" % self.taxa_count
        print "Total trees: %d" % self.tree_count
        print "Unique topologies: %d" % len(self.topologically_unique_trees)
        print "Are trees ultrametric? ", str(self.ultrametric)
        print "Mean tree age: %f" % (sum(self.tree_ages) / self.tree_count)
        return []

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()
    stat = Stat()
    plumb(stat, files)
