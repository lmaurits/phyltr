from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import TAXA_FILE_OPTIONS
from phyltr.utils.misc import read_taxa

class Grep(PhyltrCommand):
    """Usage:
        phyltr grep [taxa] [<options>] [<files>]

    Pass only those trees in a stream which contain some specified clade.

    OPTIONS:

        taxa
            A comma-separated list of taxa which must be monophyletic, or a
            Newick formatted tree structure (with no branch lengths or
            internal node names) which must be part of the tree
    """
    __options__ = TAXA_FILE_OPTIONS + [
        (
            ('-i', '--inverse', '-v'),
            dict(
                action="store_true", default=False, dest="inverse",
                help='Specify an "inverse grep": pass only those trees where the given taxa are '
                     '*not* monophyletic (cf standard Unix "grep -v")')),
    ]

    def __init__(self, **kw):
        taxa = kw.pop('taxa', None)
        PhyltrCommand.__init__(self, **kw)
        if taxa or self.opts.filename:
            self.taxa = read_taxa(taxa=taxa, filename=self.opts.filename, column=self.opts.column)
        else:
            raise ValueError("Must provide a list of taxa or a file containing such a list!")
        if len(self.taxa) == 1:
            raise ValueError("Must specify more than one taxon!")

    @classmethod 
    def init_from_opts(cls, options, files=None):
        return cls(taxa=set(files.pop(0).split(",")) if files else [], _opts=options)

    def process_tree(self, t):
        clade_leaves = [l for l in t.get_leaves() if l.name in self.taxa]
        mrca = t.get_common_ancestor(clade_leaves)
        is_mono = set(mrca.get_leaves()) == set(clade_leaves)
        if (is_mono and not self.opts.inverse) or (not is_mono and self.opts.inverse):
            return t
