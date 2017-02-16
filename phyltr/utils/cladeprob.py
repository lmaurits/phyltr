from __future__ import division

import math

class CladeProbabilities:

    def __init__(self):

        self.tree_count = 0
        self.clade_counts = {}
        self.clade_ages = {}
        self.clade_attributes = {}
        self.caches ={}

    def add_tree(self, tree):

        """Record clade counts for the given tree."""

        cache = tree.get_cached_content()
        self.tree_count += 1
        for subtree in tree.traverse():
            leaves = [leaf.name for leaf in cache[subtree]]
            if len(leaves) == 1:
                continue
            clade = ",".join(sorted(leaves))
            self.clade_counts[clade] = self.clade_counts.get(clade,0) + 1
            leaf, age = subtree.get_farthest_leaf()
            if clade in self.clade_ages:
                self.clade_ages[clade].append(age)
            else:
                self.clade_ages[clade] = [age]
            extra_features = [f for f in subtree.features if f not in ("name","dist","support")]
            for f in extra_features:
                value = getattr(subtree, f)
                try:
                    value = float(value)
                    if f not in self.clade_attributes:
                        self.clade_attributes[f] = {}
                    if clade in self.clade_attributes[f]:
                        self.clade_attributes[f][clade].append(value)
                    else:
                        self.clade_attributes[f][clade] = [value]
                except ValueError:
                    continue
        self.caches[tree] = cache

    def compute_probabilities(self):

        """Populate the self.clade_probs dictionary with probability values,
        based on the current clade and tree counts."""

        self.clade_probs = dict((c, self.clade_counts[c] / self.tree_count) for c in self.clade_counts)

    def get_tree_prob(self, t):

        """Compute the probability of a tree, as the product of the
        probabilities of all of its constituent clades according to the
        current self.clade_probs values."""

        cache = self.caches.get(t,t.get_cached_content())
        prob = 0
        for node in t.traverse():
            if node == t:
                continue
            leaves = [leaf.name for leaf in cache[node]]
            if len(leaves) == 1:
                continue
            clade = ",".join(sorted(leaves))
            prob += math.log(self.clade_probs[clade])
        return prob

    def annotate_tree(self, tree):

        """Set the support attribute of the nodes in tree using the current
        self.clade_probs values."""

        cache = self.caches.get(tree,tree.get_cached_content())
        for node in tree.traverse():
            leaves = [leaf.name for leaf in cache[node]]
            if len(leaves) == 1:
                continue
            clade = ",".join(sorted(leaves))
            node.support = self.clade_probs[clade]

    def save_clade_report(self, filename, threshold=0.0, age=False):
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
            if age:
                ages = self.clade_ages[c]
                mean = sum(ages)/len(ages)
                ages.sort()
                lower, median, upper = [ages[int(x*len(ages))] for x in 0.05,0.5,0.95]
                line = "%.4f, %.2f (%.2f-%.2f) [%s]\n" % (p, mean, lower, upper, c)
            else:
                line = "%.4f, [%s]\n" % (p, c)
            fp.write(line)
        fp.close()
