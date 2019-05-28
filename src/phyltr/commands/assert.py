from phyltr.commands.base import PhyltrCommand


class Assert(PhyltrCommand):
    """
    Print basic properties of a tree stream, such as the number of trees and taxa.
    """
    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.taxonset = None

    def process_tree(self, t, n):
        leaves = set(l.name for l in t.get_leaves())
        if n == 1:
            self.taxonset = leaves
        else:
            assert leaves == self.taxonset, 'Trees have different taxon sets'
        return t
