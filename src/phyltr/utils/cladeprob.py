import csv
import collections
import math
import statistics


def parse_float(value):
    # Some BEAST classess wrap numeric annotations in quotation marks
    while (value.startswith('"') and value.endswith('"')) or \
            (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return float(value)

def format_floats(row):
    return (("{0:0.4f}".format(x) if type(x) == float else x for x in row))

def compute_mean_median_hpd(values, interval):
    values = sorted(values)
    return (
        statistics.mean(values),
        statistics.median(values),
        [values[int(x * len(values))] for x in interval]
    )


def add_mean_median_hpd(clade, values, interval, prefix='', hpd_prefix=None, precision=None):
    """
    Annotate a tree node with summary statistics.

    :param clade: Tree node to annotate
    :param values: List of numbers to compute statistics for
    :param interval: Pair of lower/upper percentiles for HPD interval
    :param prefix: Prefix to use for the feature names
    :param hpd_prefix: Prefix to use for the HPD feature
    :param precision: Precision for formatting floating point numbers
    """
    precision = '' if precision is None else '.{}'.format(precision)
    mean, median, hpd = compute_mean_median_hpd(values, interval)
    values = sorted(values)
    clade.add_feature(prefix + 'mean', '{:{precision}f}'.format(mean, precision=precision))
    clade.add_feature(prefix + 'median', '{:{precision}f}'.format(median, precision=precision))
    clade.add_feature(
        (hpd_prefix or prefix) + "HPD",
        '{:{precision}f}-{:{precision}f}'.format(*hpd, **dict(precision=precision)))


class CladeProbabilities:

    def __init__(self):

        self.tree_count = 0
        self.clade_counts = {}
        self.clade_ages = collections.defaultdict(list)
        self.clade_attributes = collections.defaultdict(lambda: collections.defaultdict(list))
        self.leaf_heights = collections.defaultdict(list)
        self.caches = {}

    def add_tree(self, tree):

        """Record clade counts for the given tree."""

        cache = tree.get_cached_content()
        self.tree_count += 1

        # Find height of tree
        irrelevant_leaf, tree_height = tree.get_farthest_leaf()
        # Record clades
        for subtree in tree.traverse():
            leaves = [leaf.name for leaf in cache[subtree]]
            clade = " ".join(sorted(leaves))
            # Record ages of non-leaf clades
            if len(leaves) > 1:
                self.clade_counts[clade] = self.clade_counts.get(clade, 0) + 1
                self.clade_ages[clade].append(subtree.get_farthest_leaf()[1])
            extra_features = [f for f in subtree.features if f not in ("name", "dist", "support")]
            # Record annotations for all clades, even leaves
            for f in extra_features:
                try:
                    self.clade_attributes[f][clade].append(parse_float(getattr(subtree, f)))
                except ValueError:
                    continue
        # Record leaf heights
        leaf_heights = [(leaf.name, tree.get_distance(leaf)) for leaf in cache[tree]]
        tree_height = max(d for (l, d) in leaf_heights)
        for leaf, leaf_height in leaf_heights:
            self.leaf_heights[leaf].append((tree_height - leaf_height))

        self.caches[tree] = cache

    def compute_probabilities(self):
        """Populate the self.clade_probs dictionary with probability values,
        based on the current clade and tree counts."""
        self.clade_probs = {c: self.clade_counts[c] / self.tree_count for c in self.clade_counts}

    def get_tree_prob(self, t):

        """Compute the probability of a tree, as the product of the
        probabilities of all of its constituent clades according to the
        current self.clade_probs values."""

        cache = self.caches.get(t, t.get_cached_content())
        prob = 0
        for node in t.traverse():
            if node == t:
                continue
            leaves = [leaf.name for leaf in cache[node]]
            if len(leaves) == 1:
                continue
            clade = " ".join(sorted(leaves))
            prob += math.log(self.clade_probs[clade])
        return prob

    def annotate_tree(self, tree):

        """Set the support attribute of the nodes in tree using the current
        self.clade_probs values."""

        cache = self.caches.get(tree, tree.get_cached_content())
        for node in tree.traverse():
            leaves = [leaf.name for leaf in cache[node]]
            if len(leaves) == 1:
                continue
            clade = " ".join(sorted(leaves))
            node.support = self.clade_probs[clade]

    def save_clade_report(self, filename, threshold=0.0, age=False):
        clade_probs = [(self.clade_probs[c], c) for c in self.clade_probs]
        if threshold < 1.0:
            clade_probs = [(p, c) for (p, c) in clade_probs if p >= threshold]
        # Sort by clade size and then case-insensitive alpha...
        clade_probs.sort(key=lambda x:(len(x[1].split()),x[1].lower()),reverse=True)
        # ...then by clade probability
        # (this results in a list sorted by probability and then name)
        clade_probs.sort(key=lambda x: x[0], reverse=True)

        # Sanity check - the first clade in the sorted list *should* be the "everything" clade.
        if clade_probs:
            assert len(clade_probs[0][1].split()) == len(self.leaf_heights)

        fp = open(filename, "w")
        writer = csv.writer(fp)
        if age:
            writer.writerow(["support","age_mean","age_95HPD_lower","age_95HPD_upper","clade taxa"])
        else:
            writer.writerow(["support","clade taxa"])
        for p, c in clade_probs:
            if age:
                ages = self.clade_ages[c]
                mean = sum(ages)/len(ages)
                ages.sort()
                lower, median, upper = [ages[int(x*len(ages))] for x in (0.025,0.5,0.975)]
                line = "%.4f, %.2f (%.2f-%.2f) [%s]\n" % (p, mean, lower, upper, c)
                writer.writerow(format_floats([p, mean, lower, upper, c]))
            else:
                line = "%.4f, [%s]\n" % (p, c)
                writer.writerow(format_floats([p, c]))
        fp.close()
