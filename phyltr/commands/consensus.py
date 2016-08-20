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

import dendropy

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
        t = dendropy.Tree.get_from_string(line,schema="newick",rooting="default-rooted")
        cp.add_tree(t)
    cp.compute_probabilities()

    # Build consensus tree
    t = build_consensus_tree(cp, options.frequency)

    # Output
    print t.as_string(schema="newick", suppress_rooting=True, suppress_annotations=False).strip()

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
    t = dendropy.Tree()
    for l in all_leaves:
        taxon = dendropy.datamodel.taxonmodel.Taxon(l)
        node = dendropy.datamodel.treemodel.Node(taxon=taxon)
        t.seed_node.add_child(node)

    # Now recursively resolve the polytomy by greedily grouping clades
    new_seed = recursive_builder(t.seed_node, clades)
    t = dendropy.Tree(seed_node=new_seed)

    # Set branch lengths
    for node in t.postorder_node_iter():
        if node.is_leaf():
            node.annotations["age"] = 0.0
            node.annotations["age_HPD"] = "{0.00,0.00}"
            continue
        clade_str = ",".join(sorted([l.taxon.label for l in node.leaf_nodes()]))
        mean = cp.mean_clade_ages[clade_str]
        node.annotations["age"] = mean
        node.annotations["age_HPD"] = "{%.2f,%.2f}" % cp.hpd_clade_ages[clade_str]
        for child in node.child_node_iter():
            child.edge.length = mean - child.annotations.get_value("age",0.0)
    t.update_taxon_namespace()
    return t

def recursive_builder(t, clades):

    # Get a list of all my children
    children = set([child.taxon.label for child in t.child_nodes()])
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
        clade_nodes = set(t.leaf_iter(lambda l:l.taxon.label in clade))
        for l in clade_nodes:
            t.remove_child(l)
        child = dendropy.datamodel.treemodel.Node()
        child.annotations["posterior"] = p
        cladestr = ",".join(sorted(clade))
        t.add_child(child)
        for l in clade_nodes:
            child.add_child(l)
        # ...remove the children in the clade I just grouped from the list of
        # children which I still need to group
        children -= clade
        if not children:
            break
    # Resolve polytomies one level down
    for child in t.child_node_iter():
        recursive_builder(child, clades)

    return t
