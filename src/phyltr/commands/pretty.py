from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter

class Pretty(PhyltrCommand):
    """
    Print an "ASCII art" representation of a treestream.
    """
    __options__ = [
        (
            ('-c', '--compress'),
            dict(
                action="store_true", dest="compress", default=False,
                help="Compress highly supported clades to a single node")),
        (
            ('-l', '--label'),
            dict(
                default="name",
                help="The name of an attribute with which to label leaves")),
    ]

    sink = StringFormatter

    def process_tree(self, t):
        # Change node names to get the desired appearance
        for node in t.traverse():
            # Replace leaf node names with requested attribute
            if node.is_leaf() and hasattr(node, self.opts.label):
                node.name = getattr(node, self.opts.label)
            # Add support to interior nodes
            else:
                node.name = "%.2f" % node.support

        # Collapse high probability clades
        if self.opts.compress:
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

        # Ladderize
        t.ladderize()

        return t.get_ascii()
