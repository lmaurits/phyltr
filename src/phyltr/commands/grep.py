from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import TAXA_FILE_OPTIONS
from phyltr.utils.misc import read_taxa


class Grep(PhyltrCommand):
    """
    Pass only those trees in a stream which contain some specified clade.
    """
    __options__ = TAXA_FILE_OPTIONS + [
        (
            ('taxa',),
            dict(
                metavar='TAXA', nargs='*',
                help="taxa which must be monophyletic, or a Newick formatted tree structure "
                     "(with no branch lengths or internal node names) which must be part of "
                     "the tree")),
        (
            ('-i', '--inverse', '-v'),
            dict(
                action="store_true", default=False, dest="inverse",
                help='Specify an "inverse grep": pass only those trees where the given taxa are '
                     '*not* monophyletic (cf standard Unix "grep -v")')),
    ]

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        if not (self.opts.taxa or self.opts.filename):
            raise ValueError("Must provide a list of taxa or a file containing such a list!")
        if not self.opts.taxa:
            self.opts.taxa = read_taxa(self.opts.filename, column=self.opts.column)
        self.opts.taxa = set(self.opts.taxa)
        if len(self.opts.taxa) == 1:
            raise ValueError("Must specify more than one taxon!")

    def process_tree(self, t, _):
        clade_leaves = [l for l in t.get_leaves() if l.name in self.opts.taxa]
        mrca = t.get_common_ancestor(clade_leaves)
        is_mono = set(mrca.get_leaves()) == set(clade_leaves)
        if (is_mono and not self.opts.inverse) or (not is_mono and self.opts.inverse):
            return t
