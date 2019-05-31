from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import taxa_spec_options, selector_from_taxa_spec

class Prune(PhyltrCommand):
    """
    Delete a specified set of nodes from the tree.
    """
    __options__ = taxa_spec_options('delete') + [
        (
            ('-i', '--inverse'),
            dict(
                action="store_true", default=False, dest="inverse",
                help='Specify an "inverse prune": delete all taxa *except* those given in the '
                     'taxa option (or all *except* those with the given attribute value).')),
    ]

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.condition = selector_from_taxa_spec(self.opts)

    def process_tree(self, t, _):
        t.prune([l for l in t.get_leaves() if not self.condition(l)], preserve_branch_length=True)
        return t
