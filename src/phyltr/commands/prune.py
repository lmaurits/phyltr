import operator

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
            taxa = read_taxa(taxa=taxa, filename=self.opts.filename, column=self.opts.column)
            if self.opts.inverse:
                self.prune_condition = lambda l: l.name in taxa
            else:
                self.prune_condition = lambda l: l.name not in taxa
        elif self.opts.attribute and self.opts.value:
            op = operator.eq if self.opts.inverse else operator.ne
            self.prune_condition = \
                lambda l: hasattr(l, self.opts.attribute) and \
                          op(getattr(l, self.opts.attribute), self.opts.value)
        else:
            raise ValueError("Incompatible arguments")

    @classmethod 
    def init_from_opts(cls, options, files=None):
        return cls(_opts=options, taxa=set(files.pop(0).split(",")) if files else [])

    def process_tree(self, t, _):
        t.prune([l for l in t.get_leaves() if self.prune_condition(l)], preserve_branch_length=True)
        return t
