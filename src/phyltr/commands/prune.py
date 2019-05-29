import operator

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import TAXA_FILE_OPTIONS
from phyltr.utils.misc import read_taxa

class Prune(PhyltrCommand):
    """
    Delete a specified set of nodes from the tree.
    """
    __options__ = TAXA_FILE_OPTIONS + [
        (
            ('taxa',),
            dict(
                metavar='TAXA', nargs='*',
                help="Leaf taxa to delete from the tree",)),
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

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)

        if self.opts.taxa:
            pass
        elif self.opts.filename:
            self.opts.taxa = read_taxa(self.opts.filename, column=self.opts.column)

        if self.opts.taxa:
            if self.opts.inverse:
                self.prune_condition = lambda l: l.name in self.opts.taxa
            else:
                self.prune_condition = lambda l: l.name not in self.opts.taxa
        elif self.opts.attribute and self.opts.value:
            op = operator.eq if self.opts.inverse else operator.ne
            self.prune_condition = \
                lambda l: hasattr(l, self.opts.attribute) and \
                          op(getattr(l, self.opts.attribute), self.opts.value)
        else:
            raise ValueError("Incompatible arguments")

    def process_tree(self, t, _):
        t.prune([l for l in t.get_leaves() if self.prune_condition(l)], preserve_branch_length=True)
        return t
