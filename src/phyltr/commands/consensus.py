import ete3

from phyltr.commands.base import PhyltrCommand
import phyltr.utils.cladeprob
from phyltr.utils.phyltroptparse import VALID_LENGTHS, length_option


class Consensus(PhyltrCommand):
    """
    Produce a majority rules consensus tree for the tree stream.
    """
    __options__ = [
        (
            ('-f', '--frequency'),
            dict(
                type=float, dest="frequency", default=0.5,
                help="Minimum clade frequency to include in the consensus tree.")),
        length_option('The method used to compute branch lengths for the consensus tree.'),
    ]

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t, _):
        self.cp.add_tree(t)

    def postprocess(self, _):
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
            if p >= self.opts.frequency:
               clades.append((p, set(clade.split())))
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
        clades = sorted([(len(clade), p, clade) for p, clade in clades], reverse=True)

        # Start out with a tree in which all leaves are joined in one big polytomy
        t = ete3.Tree()
        for l in all_leaves:
            t.add_child(name=l)

        # Now recursively resolve the polytomy by greedily grouping clades
        while clades:
            n, p, clade = clades.pop()
            # Pluck the children from the root which comprise this clade
            clade_nodes = [
                node for node in t.get_children()
                if set((l.name for l in node.get_leaves())).issubset(set(clade))]
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
            assert n.support >= self.opts.frequency
            if n.is_leaf():
                assert n.name

        # Add age annotations
        cache = t.get_cached_content()
        for clade in t.traverse("postorder"):
            clade_key = " ".join(sorted([l.name for l in cache[clade]]))
            if not clade.is_leaf():
                # Compute age statistics and annotate tree
                ages = self.cp.clade_ages[clade_key]
                phyltr.utils.cladeprob.add_mean_median_hpd(clade, ages, 'age_')

                # Choose the canonical age for this clade
                clade_age = VALID_LENGTHS[self.opts.lengths](ages)
                # Set branch lengths accordingly
                for child in clade.get_children():
                    _, child_height = child.get_farthest_leaf()
                    child.dist = clade_age - child_height

            for f in self.cp.clade_attributes:
                phyltr.utils.cladeprob.add_mean_median_hpd(
                    clade, self.cp.clade_attributes[f][clade_key], prefix=f + '_')

        # Correct leaf heights
        for leaf in cache[t]:
            # Choose the canonical height for this leaf
            # HUOM!  At first glance this code may look "backward" with regard to max and min.
            # But note that maximising/minimising the height of a leaf above the "contemporaneous"
            # line corresponds to minimising/maximising its originate branch length, respectively.
            # In order to treat the self.lengths parameter consistently, "max" should mean maximum
            # branch length and therefore *minimum* leaf height (leaf height being the thing we
            # actually keep track of, because it's what people typically calibrate on).
            if self.opts.lengths == 'max':
                func = min
            elif self.opts.lengths == 'min':
                func = max
            else:
                func = VALID_LENGTHS[self.opts.lengths]
            leaf.dist -= func(self.cp.leaf_heights[leaf.name])
            #assert leaf.dist >= 0
        # Done!
        return t

    def enforce_consistency(self, clades):
        # We don't need to worry about this if we only have clades
        # that are supported at 0.5 or above, as these are
        # guaranteed to be consistent
        if self.opts.frequency >= 0.5:
            return clades

        # First, find the index of the first clade which is potentially
        # problematic
        n = -1
        for n, (p, c) in enumerate(clades):
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
                        clades.remove((p, susp))
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
