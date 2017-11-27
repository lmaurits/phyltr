"""Usage:
    phyltr consensus [<options>] [<files>]

Produce a majority rules consensus tree for the tree stream.

OPTIONS:

    -f, --frequency
        Minimum clade frequency to include in the consensus tree (default 0.5)

    -l, --length
        Specifies the method used to compute branch lengths for the consensus
        tree.  Must be one of: "max", "mean", "median", or "min".  Default is
        mean.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import ete3

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser
import phyltr.utils.cladeprob

class Consensus(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr consensus")
    parser.add_option('-f', '--frequency', type="float",dest="frequency", default=0.5, help="Minimum clade support to include in tree.")
    parser.add_option('-l', '--lengths', action="store", dest="lengths", default="mean")

    def __init__(self, frequency=0.5, lengths="mean"):
        self.frequency = frequency
        if lengths in ("max", "mean", "median", "min"):
            self.lengths = lengths
        else:
            raise ValueError("--lengths option must be one of max, mean, median or min!")
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    @classmethod 
    def init_from_opts(cls, options, files=[]):
        consensus = Consensus(options.frequency, options.lengths)
        return consensus

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
        # Pop the clade with highest probability, which *should* be the clade
        # with support 1.0 containing all leaves
        taxon_count, prob, all_leaves = clades.pop()
        assert prob == 1.0
        assert all((taxon_count > count for count, p, clade in clades))
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
            clade_key = ",".join(sorted([l.name for l in cache[clade]]))
            if not clade.is_leaf(): # all leaves have age zero, so don't bother
                # Compute age statistics and annotate tree
                ages = self.cp.clade_ages[clade_key]
                ages.sort()
                mean = sum(ages)/len(ages)
                lower, median, upper = [ages[int(x*len(ages))] for x in (0.05,0.5,0.95)]
                clade.add_feature("age_mean", mean)
                clade.add_feature("age_median", median)
                clade.add_feature("age_HPD", "{%f-%f}" % (lower,upper))
                # Choose the canonical age for this clade
                if self.lengths == "max":
                    age = max(ages)
                elif self.lengths == "mean":
                    age = sum(ages) / len(ages)
                elif self.lengths == "median":
                    age = median
                elif self.lengths == "min":
                    age = min(ages)
                # Set branch lengths accordingly
                for c in clade.get_children():
                    leaf, age = c.get_farthest_leaf()
                    c.dist = mean - age

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
