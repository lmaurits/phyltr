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

from phyltr.commands.generic import PhyltrCommand, plumb_strings

import phyltr.utils.phyoptparse as optparse

class Pretty(PhyltrCommand):

    def __init__(self, compress=False):
        self.compress = compress

    def process_tree(self, t):
        # Add support to interior nodes
        for node in t.traverse():
            if not node.is_leaf():
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

def run():
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-c', '--compress', action="store_true", dest="compress", default=False)
    options, files = parser.parse_args()
    
    pretty = Pretty(compress=options.compress)
    plumb_strings(pretty, files)
