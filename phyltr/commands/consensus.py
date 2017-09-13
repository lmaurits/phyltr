"""Usage:
    phyltr consensus [<options>] [<files>]

Produce a majority rules consensus tree for the tree stream.

OPTIONS:

    -f, --frequency
        Minimum clade frequency to include in the consensus tree (default 0.t)

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import ete3

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin
import phyltr.utils.cladeprob

class Consensus(PhyltrCommand):

    def __init__(self, frequency=0.5):
        self.frequency = frequency
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t):
        self.cp.add_tree(t)

    def postprocess(self):
        self.cp.compute_probabilities()
        # Build consensus tree
        t = self.build_consensus_tree()
        yield t

    def build_consensus_tree(self):

        # Build a list of all clades in the treestream with frequency above the
        # requested threshold, sorted first by size and then by frequency.  Do not
        # include the trivial clade of all leaves.
        clades = []
        for clade, p in self.cp.clade_probs.items():
            if p >= self.frequency:
                clade = clade.split(",")
                clades.append((len(clade), p, set(clade)))
        clades.sort()
        junk, trash, all_leaves = clades.pop()
        clades.reverse()

        # Start out with a tree in which all leaves are joined in one big polytomy
        t = ete3.Tree()
        for l in all_leaves:
            t.add_child(name=l)

        # Now recursively resolve the polytomy by greedily grouping clades
        t = recursive_builder(t, clades)
        cache = t.get_cached_content()

        # Add age annotations
        for clade in t.traverse("postorder"):
            if clade.is_leaf():
                continue
            clade_key = ",".join(sorted([l.name for l in cache[clade]]))
            ages = self.cp.clade_ages[clade_key]
            mean = sum(ages)/len(ages)
            for c in clade.get_children():
                leaf, age = c.get_farthest_leaf()
                c.dist = mean - age
            ages.sort()
            lower, median, upper = [ages[int(x*len(ages))] for x in (0.05,0.5,0.95)]
            clade.add_feature("age_mean", mean)
            clade.add_feature("age_median", median)
            clade.add_feature("age_HPD", "{%f-%f}" % (lower,upper))

            for f in self.cp.clade_attributes:
                values = self.cp.clade_attributes[f][clade_key]
                mean = sum(values)/len(values)
                values.sort()
                lower, median, upper = [values[int(x*len(values))] for x in (0.025,0.5,0.975)]
                clade.add_feature("%s_mean" % f, mean)
                clade.add_feature("%s_median" % f, median)
                clade.add_feature("%s_HPD" % f, "{%f-%f}" % (lower,upper))
        return t

def recursive_builder(t, clades):

    # Get a list of all my children
    children = set([c.name for c in t.get_children()])
    # For as long as it's possible...
    while True:
        matched = False
        # ...find the largest clade which is a subset of my children
        for length, p, clade in clades:
            if len(clade) == 1:
                continue
            if clade.issubset(children):
                matched = True
                break
        if not matched:
            break
        # ...remove the children in that clade and add them under a new child
        clades.remove((length, p, clade))
        clade_nodes = set([t.get_leaves_by_name(l)[0] for l in clade])
        for l in clade_nodes:
            t.remove_child(l)
        child = t.add_child()
        child.support = p
        for l in clade_nodes:
            child.add_child(l)
        # ...remove the children in the clade I just grouped from the list of
        # children which I still need to group
        children -= clade
        if not children:
            break
    # Resolve polytomies one level down
    for child in t.get_children():
        recursive_builder(child, clades)
    return t


def init_from_args(*args):
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--frequency', type="float",dest="frequency", default=0.5, help="Minimum clade support to include in tree.")
    options, files = parser.parse_args(*args)

    consensus = Consensus(options.frequency)
    return consensus, files

def run():
    consensus, files = init_from_args()
    plumb_stdin(consensus, files)

