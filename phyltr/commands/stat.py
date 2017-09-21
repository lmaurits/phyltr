"""Usage:
    phyltr stat [<files>]

Print basic properties of a tree stream, such as the number of trees and taxa.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import optparse

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import NullSink
from phyltr.utils.topouniq import are_same_topology

class Stat(PhyltrCommand):

    sink = NullSink

    parser = optparse.OptionParser(add_help_option = False)
    parser.add_option('-h', '--help', action="store_true", dest="help", default=False)

    def __init__(self):

        self.tree_count = 0
        self.taxa_count = 0
        self.ultrametric = True
        self.topologically_unique_trees = []
        self.tree_ages = []
        self.firsttree = True

    @classmethod 
    def init_from_opts(cls, options, files):
        stat = Stat()
        return stat

    def process_tree(self, t):
        # Stuff we do to every tree...
        self.tree_count += 1
        leaves = t.get_leaves()
        leave_ages = [t.get_distance(l) for l in leaves]
        self.tree_ages.append(t.get_farthest_leaf()[1])
        if abs(max(leave_ages) - min(leave_ages)) > max(leave_ages)/1000.0:
            self.ultrametric = False
        # Stuff we only do to the first tree...
        if self.firsttree:
            self.firsttree = False
            self.taxa_count = len(leaves)
            self.topologically_unique_trees.append(t)
        # Stuff we only do to trees *other* than the first...
        else:
            for u in self.topologically_unique_trees:
                if are_same_topology(t, u):
                    break
            else:
                self.topologically_unique_trees.append(t)
        return t

    def postprocess(self):
        self.topology_count = len(self.topologically_unique_trees)
        self.min_tree_height = min(self.tree_ages)
        self.max_tree_height = max(self.tree_ages)
        self.mean_tree_height = sum(self.tree_ages) / self.tree_count
        return []

    def post_print(self):

        print("Total taxa: %d" % self.taxa_count)
        print("Total trees: %d" % self.tree_count)
        print("Unique topologies: %d" % self.topology_count)
        print("Are trees ultrametric? %s" % str(self.ultrametric))
        print("Mean tree height: %f" % self.mean_tree_height)
        print("Min tree height: %f" % self.min_tree_height)
        print("Max tree height: %f" % self.max_tree_height)
