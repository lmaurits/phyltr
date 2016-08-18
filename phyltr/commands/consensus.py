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

import fileinput

import ete2

import phyltr.utils.phyoptparse as optparse
import phyltr.utils.cladeprob

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--frequency', type="float",dest="frequency", default=0.5, help="Minimum clade support to include in tree.")
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        cp.add_tree(t)
    cp.compute_probabilities()

    # Build consensus tree
    t = build_consensus_tree(cp, options.frequency)

    # Output
    print t.write()

    # Done
    return 0

def build_consensus_tree(cp, threshold):

    # Build a list of all clades in the treestream with frequency above the
    # requested threshold, sorted first by size and then by frequency.  Do not
    # include the trivial clade of all leaves.
    clades = []
    for clade, p in cp.clade_probs.items():
        if p >= threshold:
            clade = clade.split(",")
            clades.append((len(clade), p, set(clade)))
    clades.sort()
    junk, trash, all_leaves = clades.pop()
    clades.reverse()

    # Start out with a tree in which all leaves are joined in one big polytomy
    t = ete2.Tree()
    for l in all_leaves:
        t.add_child(name=l)

    # Now recursively resolve the polytomy by greedily grouping clades
    return recursive_builder(t, clades)

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
