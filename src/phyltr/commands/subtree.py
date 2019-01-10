"""Usage:
    phyltr subtree [taxa] [<options>] [<files>]

Replace each tree with the minimal subtree containing the specified taxa.
Unlike an inverse prune, this may change the height of the tree.

OPTIONS:

    taxa
        A comma-separated list of leaf taxa to keep in the tree

    -a, --attribute
        An attribute to inspect to decide which leaves to keep.  Must be used
        in conjunction with --values.

    -v, --values
        A comma-separated list of values of the attribute specified with
        --attribute, which specifies which taxa to keep.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class Subtree(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr subtree")
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-v', '--values', default=None)

    def __init__(self, taxa=None, filename=None, attribute=None, values=None):
        self.attribute = attribute
        self.filename = filename
        self.values = values

        self.by_attribute = False

        if taxa:
            self.taxa = taxa
        elif filename:
            with open(self.filename, "r") as fp:
                self.taxa = [t.strip() for t in fp.readlines()]
            if not self.taxa:
                raise ValueError("Empty file!")
        elif self.attribute and self.values:
            self.taxa = []
            self.values = values.split(",")
        else:
            raise ValueError("Incompatible arguments")

    @classmethod 
    def init_from_opts(cls, options, files):
        if files:
            taxa = set(files.pop(0).split(","))
        else:
            taxa = []
        subtree = Subtree(taxa, options.filename, options.attribute, options.values)
        return subtree

    def process_tree(self, t):
        if self.taxa:
            leaves = [l for l in t.get_leaves() if l.name in self.taxa]
            mrca = leaves[0].get_common_ancestor(leaves[1:])
            t = mrca
            new_tree_leaves = [l.name for l in t.get_leaves()]
            assert all((t in new_tree_leaves for t in self.taxa))
        else:
            taxa = [l for l in t.get_leaves() if hasattr(l,self.attribute) and getattr(l,self.attribute) in self.values]
            mrca = taxa[0].get_common_ancestor(taxa[1:])
            t = mrca
        return t
