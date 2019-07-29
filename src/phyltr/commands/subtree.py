from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import taxa_spec_options, selector_from_taxa_spec


class Subtree(PhyltrCommand):
    """
    Replace each tree with the minimal subtree containing the specified taxa.
    Unlike an inverse prune, this may change the height of the tree.
    """
    __options__ = taxa_spec_options('keep')

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.condition = selector_from_taxa_spec(self.opts)

    def process_tree(self, t, _):
        return t.get_common_ancestor([l for l in t.get_leaves() if self.condition(l)])
