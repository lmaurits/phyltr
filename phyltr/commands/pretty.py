"""Usage:
    phyltr pretty [<options>] [<files>]

Print an "ASCII art" representation of a treestream.

OPTIONS:

    -c, --compress
        Compress highly supported clades to a single node

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import dendropy

from phyltr.utils.treestream_io import read_tree, write_tree
import phyltr.utils.phyoptparse as optparse

def run():
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-c', '--compress', action="store_true", dest="compress", default=False)
    options, files = parser.parse_args()

    # Read trees
    for line in fileinput.input(files):
        t = read_tree(line)

        # Add support to interior nodes
        for node in t.seed_node.preorder_internal_node_iter():
            for name in ("posterior","support"):
                if node.annotations.get_value(name,None):
                    node.label = "(%.2f)" % float(node.annotations[name])

        # Collapse high probability clades
        if options.compress:
            dead_nodes = []
            for node in t.preorder_internal_node_iter():
                if node in dead_nodes or node.is_leaf():
                    continue
                desc = list(node.preorder_iter())
                if all([float(n.annotations.get_value("posterior",0.0)) >=0.9 for n in desc]):
                    dead_nodes.extend(desc)
                    node.label = "(%.2f) %s" % (float(n.annotations["posterior"]), "+".join(sorted([l.taxon.label for l in node.leaf_iter()])))
                    for child in node.child_node_iter():
                        node.remove_child(child)
        print t.as_ascii_plot(width=80,show_internal_node_labels=True)

    return 0
