"""Usage:
    phyltr grep [taxa] [<options>] [<files>]

Pass only those trees in a stream which contain some specified clade.

OPTIONS:

    taxa
        A comma-separated list of taxa which must be monophyletic, or a
        Newick formatted tree structure (with no branch lengths or
        internal node names) which must be part of the tree

    -f, --file
        A file specifying which taxa must be monophyletic.  One taxon
        name per line.

    -i, --inverse, -v
        Specify an "inverse grep": pass only those trees where the given taxa
        are *not* monophyletic (cf standard Unix "grep -v")

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class Grep(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr grep")
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-i', '--inverse', action="store_true", default=False, dest="inverse")
    parser.add_option('-v', action="store_true", default=False, dest="inverse")

    def __init__(self, taxa=None, filename=None, inverse=False):
        self.filename = filename
        self.inverse = inverse

        if taxa:
            self.taxa = taxa
        elif filename:
            with open(self.filename, "r") as fp:
                self.taxa = set([t.strip() for t in fp.readlines()])
            if not self.taxa:
                raise ValueError("Empty file!")
        else:
            raise ValueError("Must provide a list of taxa or a file containing such a list!")
        if len(taxa) == 1:
            raise ValueError("Must specify more than one taxon!")

    @classmethod 
    def init_from_opts(cls, options, files=None):
        if files:
            taxa = set(files.pop(0).split(","))
        else:
            taxa = []

        return cls(taxa, options.filename, options.inverse)

    def process_tree(self, t):
        clade_leaves = [l for l in t.get_leaves() if l.name in self.taxa]
        mrca = t.get_common_ancestor(clade_leaves)
        is_mono = set(mrca.get_leaves()) == set(clade_leaves)
        if (is_mono and not self.inverse) or (not is_mono and self.inverse):
            return t
