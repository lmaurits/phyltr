from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter


class Sibling(PhyltrCommand):
    """
    Print the sibling of a specific taxon for each tree in a stream.
    """
    sink = StringFormatter
    __options__ = [
        (('taxon',), dict(help='The name of a leaf taxon whose sibling to print'))
    ]

    def process_tree(self, t, _):
        # Find our taxon
        try:
            taxon = t.get_leaves_by_name(self.opts.taxon)[0]
        except IndexError:
            raise ValueError("Taxon %s not found in tree?" % self.opts.taxon)

        # Get its sister - note we are assuming a binary tree here, how to generalise?
        sister = taxon.get_sisters()[0]

        # Format string representation of sister node
        if sister.is_leaf():
            return sister.name
        return "({0})".format(",".join(sorted(sister.get_leaf_names())))
