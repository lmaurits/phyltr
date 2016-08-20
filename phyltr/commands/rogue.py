"""Usage:
    phyltr rogue [<options>] [<files>]

Remove rogue taxa which assume many contradictory locations in a treestream,
lowering clade supports.

OPTIONS:

    -n
        The number of rogue taxa to remove.

    -g, --guard
        A comma-separated list of taxa names which should be guarded from
        removal by the rogue searching algorithm

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import sys

import ete2

import phyltr.utils.cladeprob
import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-n', action="store", dest="iterations", type="int", default=1)
    parser.add_option('-g', "--guard", action="store", dest="guarded")
    options, files = parser.parse_args()

    # Get list of guarded taxa
    if options.guarded:
        guarded_taxa = options.guarded.split(",")
    else:
        guarded_taxa = []

    # Read trees
    trees = []
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        trees.append(t)

    # Remove rogue nodes
    for i in range(0, options.iterations):
        rogue = remove_rogue(trees, guarded_taxa)
        sys.stderr.write("Removing %s as rogue\n" % rogue)

    # Output
    for t in trees:
        print t.write()

    # Done
    return 0

def remove_rogue(trees, guarded):

    leaves = trees[0].get_leaves()
    candidates = [l for l in leaves if l.name not in guarded]
    scores = []
    # Compute maximum clade credibility for each candidate rogue
    for candidate in candidates:
        # Make a list of trees which have had candidate removed
        pruned_trees = [t.copy() for t in trees]
        survivors = set(leaves) - set(candidate)
        for pruned in pruned_trees:
            pruned.prune([s.name for s in survivors])

        # Compute clade probs
        cp = phyltr.utils.cladeprob.CladeProbabilities()
        for t in pruned_trees:
            cp.add_tree(t)
        cp.compute_probabilities()

        # Find max clade prob tree
        max_prob = -sys.float_info.max
        for t in pruned_trees:
            prob = cp.get_tree_prob(t)
            if prob > max_prob:
                max_prob = prob

        # Record
        scores.append((max_prob,candidate))

    # Find the candidate with the highest maximum clade credibility
    scores.sort()
    scores.reverse()
    rogue = scores[0][1]

    # Prune trees
    for t in trees:
        leaves = t.get_leaves()
        rogue = t.get_leaves_by_name(rogue.name)[0]
        survivors = set(leaves) - set(rogue)
        t.prune(survivors)

    return rogue.name
