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
        # requested threshold, sorted by frequency.  Do not include the trivial
        # clade of all leaves.
        clades = []
        for clade, p in self.cp.clade_probs.items():
            if p >= self.frequency:
                clade = clade.split(",")
                clades.append((p, set(clade)))
        clades.sort()

        # Pop the clade with highest probability, which *should* be the clade
        # with support 1.0 containing all leaves
        prob, all_leaves = clades.pop()
        assert prob == 1.0
        clades.reverse()

        # If our threshold is below 0.5, it is possible that the set of clades
        # we just built contains clades which contradict one another.  Remove
        # these, by removing clades which conflict with higher supported clades
        clades = self.enforce_consistency(clades)

        # Now sort the surviving clades by size, to make building the consensus
        # tree easier
        clades = [(len(clade), p, clade) for p, clade in clades]
        clades.sort()
        clades.reverse()

        # Start out with a tree in which all leaves are joined in one big polytomy
        t = ete3.Tree()
        for l in all_leaves:
            t.add_child(name=l)

        # Now recursively resolve the polytomy by greedily grouping clades
        while clades:
            n, p, clade = clades.pop()
            # Pluck the children from the root which comprise this clade
            clade_nodes = [node for node in t.get_children() if set((l.name for l in node.get_leaves())).issubset(set(clade))]
            if len(clade_nodes) == 1:
                continue
            assert clade_nodes
            for l in clade_nodes:
                t.remove_child(l)
            # Reattach them as descendents of a new child
            child = t.add_child()
            child.support = p
            for l in clade_nodes:
                child.add_child(l)

        # Check all is right with the world
        for n in t.traverse():
            assert len(n.get_children()) != 1
            assert n.support >= self.frequency
            if n.is_leaf():
                assert n.name

        # Add age annotations
        cache = t.get_cached_content()
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
                    clade_age = max(ages)
                elif self.lengths == "mean":
                    clade_age = sum(ages) / len(ages)
                elif self.lengths == "median":
                    clade_age = median
                elif self.lengths == "min":
                    clade_age = min(ages)
                # Set branch lengths accordingly
                for child in clade.get_children():
                    irrelevant_leaf, child_height = c.get_farthest_leaf()
                    child.dist = clade_age - child_height

            for f in self.cp.clade_attributes:
                values = self.cp.clade_attributes[f][clade_key]
                mean = sum(values)/len(values)
                values.sort()
                lower, median, upper = [values[int(x*len(values))] for x in (0.025,0.5,0.975)]
                clade.add_feature("%s_mean" % f, mean)
                clade.add_feature("%s_median" % f, median)
                clade.add_feature("%s_HPD" % f, "{%f-%f}" % (lower,upper))

        return t

    def enforce_consistency(self, clades):
        # We don't need to worry about this if we only have clades
        # that are supported at 0.5 or above, as these are
        # guaranteed to be consistent
        if self.frequency >= 0.5:
            return clades

        # First, find the index of the first clade which is potentially
        # problematic
        for n, (p,c) in enumerate(clades):
            if p < 0.5:
                break

        # Now compare the first potentially problematic clade to all
        # previous (i.e. more highly supported) clades and discard it
        # if it conflicts with any of them.  Once we've found a clade
        # compatible with all previous clades, iterate down to the next
        # least supported clade and compare it to all previous clades,
        # including the one we just accepted.  Rinse, repeat.
        #
        # This is not terribly clear or Pythonic code.
        # If you can see how to make it better without sacrificing
        # speed or correctness, feel free!
        while True:
            accepted = clades[0:n]
            dubious = clades[n:]
            if not dubious:
                break
            for p, susp in dubious:
                for q, good in accepted:
                    if not test_clade_compat(good, susp):
                        clades.remove((p,susp))
                        break
                else:
                    n += 1
                    break

        return clades

def test_clade_compat(good, susp):
    good = set(good)
    susp = set(susp)
    if len(good.intersection(susp)) == 0:
        return True
    elif good.issubset(susp) or susp.issubset(good):
        return True
    return False
