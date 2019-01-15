"""Usage:
    phyltr sibling taxon [<options>] [<files>]

Print the sibling of a specific taxon for each tree in a stream.

OPTIONS:

    taxon
        The name of a leaf taxon whose sibling to print

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter
from phyltr.utils.phyltroptparse import OptionParser

class Sibling(PhyltrCommand):

    sink = StringFormatter

    parser = OptionParser(__doc__, prog="phyltr sibling")

    def __init__(self, taxon=None):
        if not taxon:
            raise ValueError("Taxon required!")
        self.taxon = taxon

    @classmethod 
    def init_from_opts(cls, options, files):
        if files:
            taxon = files.pop(0)
        else:    
            taxon = None
        return cls(taxon)

    def process_tree(self, t):
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
