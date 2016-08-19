from __future__ import division

import math

class CladeProbabilities:

    def __init__(self):

        self.clade_counts = {}
        self.tree_count = 0

    def add_tree(self, tree):

        """Record clade counts for the given tree."""

        self.tree_count += 1
        for subtree in tree.seed_node.postorder_iter():
            leaf_names = [l.taxon.label for l in subtree.leaf_nodes()]
            if len(leaf_names) == 1:
                continue
            clade = ",".join(sorted(leaf_names))
            self.clade_counts[clade] = self.clade_counts.get(clade,0) + 1

    def compute_probabilities(self):

        """Populate the self.clade_probs dictionary with probability values,
        based on the current clade and tree counts."""

        self.clade_probs = dict((c, self.clade_counts[c] / self.tree_count) for c in self.clade_counts)

    def get_tree_prob(self, t):

        """Compute the probability of a tree, as the product of the
        probabilities of all of its constituent clades according to the
        current self.clade_probs values."""

        prob = 0
        for clade in t.seed_node.postorder_iter():
            if clade == t.seed_node:
                continue
            leaf_names = [l.taxon.label for l in clade.leaf_nodes()]
            if len(leaf_names) == 1:
                continue
            clade = ",".join(sorted(leaf_names))
            prob += math.log(self.clade_probs[clade])
        return prob

    def annotate_tree(self, t):

        """Set the support attribute of the nodes in tree using the current
        self.clade_probs values."""

        for clade in t.seed_node.postorder_iter():
            leaf_names = [l.taxon.label for l in clade.leaf_nodes()]
            if len(leaf_names) == 1:
                continue
            clade = ",".join(sorted(leaf_names))
            node.annotations["posterior"] = self.clade_probs[clade]

    def save_clade_report(self, filename, threshold=0.0):
        clade_probs = [(self.clade_probs[c], c) for c in self.clade_probs]
        if threshold < 1.0:
            clade_probs = [(p, c) for (p, c) in clade_probs if p >= threshold]
        # Sort by clade string, ignoring case...
        clade_probs.sort(key=lambda x:x[1].lower())
        # ...then by clade probability
        # (this results in a list sorted by probability and then name)
        clade_probs.sort(key=lambda x:x[0],reverse=True)

        fp = open(filename, "w")
        for p, c in clade_probs:
            line = "%.4f: [%s]\n" % (p, c)
            fp.write(line)
        fp.close()
