from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter

class Sibling(PhyltrCommand):
    """Usage:
        phyltr sibling taxon [<options>] [<files>]

    Print the sibling of a specific taxon for each tree in a stream.

    OPTIONS:

        taxon
            The name of a leaf taxon whose sibling to print
    """
    sink = StringFormatter

    def __init__(self, taxon=None, **kw):
        PhyltrCommand.__init__(self, **kw)
        if not taxon:
            raise ValueError("Taxon required!")
        self.taxon = taxon

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(taxon=files.pop(0) if files else None)

    def process_tree(self, t, _):
        # Find our taxon
        try:
            taxon = t.get_leaves_by_name(self.taxon)[0]
        except IndexError:
            raise ValueError("Taxon %s not found in tree?" % self.taxon)

        # Get its sister - note we are assuming a binary tree here, how to generalise?
        sister = taxon.get_sisters()[0]

        # Format string representation of sister node
        if sister.is_leaf():
            return sister.name
        else:
            return "(" + ",".join(sorted((sister.get_leaf_names()))) + ")"
