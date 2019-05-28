from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import TAXA_FILE_OPTIONS
from phyltr.utils.misc import read_taxa

class Subtree(PhyltrCommand):
    """Usage:
        phyltr subtree [taxa] [<options>] [<files>]

    Replace each tree with the minimal subtree containing the specified taxa.
    Unlike an inverse prune, this may change the height of the tree.

    OPTIONS:

        taxa
            A comma-separated list of leaf taxa to keep in the tree
    """
    __options__ = TAXA_FILE_OPTIONS + [
        (
            ('-a', '--attribute'),
            dict(
                default=None,
                help='An attribute to inspect to decide which leaves to keep.  Must be used in '
                     'conjunction with --values.')),
        (
            ('-v', '--values'),
            dict(
                default=None,
                help='A comma-separated list of values of the attribute specified with '
                     '--attribute, which specifies which taxa to keep.')),
    ]

    def __init__(self, taxa=None, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.by_attribute = False

        if taxa or self.opts.filename:
            self.taxa = read_taxa(taxa=taxa, filename=self.opts.filename, column=self.opts.column)
        elif self.opts.attribute and self.opts.values:
            self.taxa = []
            self.opts.values = self.opts.values.split(",")
        else:
            raise ValueError("Incompatible arguments")

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(taxa=set(files.pop(0).split(",")) if files else [], _opts=options)

    def process_tree(self, t):
        if self.taxa:
            leaves = [l for l in t.get_leaves() if l.name in self.taxa]
            mrca = t.get_common_ancestor(leaves)
            t = mrca
        else:
            taxa = [l for l in t.get_leaves() if hasattr(l,self.opts.attribute) and getattr(l,self.opts.attribute) in self.opts.values]
            mrca = t.get_common_ancestor(taxa)
            t = mrca
        return t
