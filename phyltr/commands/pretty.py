"""Usage:
    phyltr pretty [<options>] [<files>]

Print an "ASCII art" representation of a treestream.

OPTIONS:

    -c, --compress
        Compress highly supported clades to a single node

    -l, --label
        Specify the name of an attribute with which to label leaves

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_strings

class Pretty(PhyltrCommand):

    def __init__(self, label="name", compress=False):
        self.label = label
        self.compress = compress

    def process_tree(self, t):
        # Change node names to get the desired appearance
        for node in t.traverse():
            # Replace leaf node names with requested attribute
            if node.is_leaf() and hasattr(node, self.label):
                node.name = getattr(node, self.label)
            # Add support to interior nodes
            else:
                node.name = "%.2f" % node.support

        # Collapse high probability clades
        if self.compress:
            dead_nodes = []
            for node in t.traverse("preorder"):
                if node in dead_nodes or node.is_leaf():
                    continue
                desc = node.get_descendants()
                desc.append(node)
                if all([n.support >=0.9 for n in desc]):
                    dead_nodes.extend(desc)
                    node.name = "(%.2f) %s" % (node.support, "+".join(sorted([l.name for l in node.get_leaves()])))
                    for child in node.get_children():
                        child.detach()

        return t.get_ascii()

def init_from_args(*args):
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-c', '--compress', action="store_true", dest="compress", default=False)
    parser.add_option('-l', '--label', default="name")
    options, files = parser.parse_args(*args)
    
    pretty = Pretty(label=options.label, compress=options.compress)
    return pretty, files

def run():
    pretty, files = init_from_args()
    plumb_strings(pretty, files)
