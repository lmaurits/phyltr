from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import TAXA_FILE_OPTIONS
from phyltr.utils.misc import read_taxa

class Prune(PhyltrCommand):
    """Usage:
        phyltr prune [taxa] [<options>] [<files>]

    Delete a specified set of nodes from the tree.

    OPTIONS:

        taxa
            A comma-separated list of leaf taxa to delete from the tree
    """
    __options__ = TAXA_FILE_OPTIONS + [
        (
            ('-a', '--attribute'),
            dict(
                default=None,
                help="An attribute to inspect to decide which leaves to prune.  Must be used in "
                     "conjunction with --value.")),
        (
            ('-i', '--inverse'),
            dict(
                action="store_true", default=False, dest="inverse",
                help='Specify an "inverse prune": delete all taxa *except* those given in the '
                     'taxa option (or all *except* those with the given attribute value).')),
        (
            ('-v', '--value'),
            dict(
                default=None,
                help="The value of the attribute specified with --attribute which specifies which "
                     "taxa to prune.")),
    ]

    def __init__(self, taxa=None, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.by_attribute = False

        if taxa or self.opts.filename:
            self.taxa = read_taxa(taxa=taxa, filename=self.opts.filename, column=self.opts.column)
        elif self.opts.attribute and self.opts.value:
            self.taxa = []
        else:
            raise ValueError("Incompatible arguments")

    @classmethod 
    def init_from_opts(cls, options, files=None):
        return cls(_opts=options, taxa=set(files.pop(0).split(",")) if files else [])

    def process_tree(self, t, _):
        if self.taxa:
            # Pruning by a list of taxa
            if self.opts.inverse:
                pruning_taxa = [l for l in t.get_leaves() if l.name in self.taxa]
            else:
                pruning_taxa = [l for l in t.get_leaves() if l.name not in self.taxa]
        else:
            # Pruning by an attribute value
            if self.opts.inverse:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,self.opts.attribute) and getattr(l,self.opts.attribute) == self.opts.value]
            else:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,self.opts.attribute) and getattr(l,self.opts.attribute) != self.opts.value]
        # Do the deed
        t.prune(pruning_taxa, preserve_branch_length=True)
        return t
