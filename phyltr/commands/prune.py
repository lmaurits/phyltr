"""Usage:
    phyltr prune [taxa] [<options>] [<files>]

Delete a specified set of nodes from the tree.

OPTIONS:

    taxa
        A comma-separated list of leaf taxa to delete from the tree

    -a, --attribute
        An attribute to inspect to decide which leaves to prune.  Must be used
        in conjunction with --value.

    -f, --file
        A file specifying which leaf taxa to delete from the tree.  One taxon
        name per line.

    -i, --inverse
        Specify an "inverse prune": delete all taxa *except* those given in
        the taxa option (or all *except* those with the given attribute value).

    -v, --value
        The value of the attribute specified with --attribute which specifies
        which taxa to prune.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class Prune(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr prune")
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-i', '--inverse', action="store_true", default=False, dest="inverse")
    parser.add_option('-v', '--value', default=None)

    def __init__(self, taxa=None, filename=None, attribute=None, value=None, inverse=False):
        self.attribute = attribute
        self.filename = filename
        self.inverse = inverse
        self.value = value

        self.by_attribute = False

        if taxa:
            self.taxa = taxa
        elif filename:
            with open(self.filename, "r") as fp:
                self.taxa = set([t.strip() for t in fp.readlines()])
            if not self.taxa:
                raise ValueError("Empty file!")
        elif self.attribute and self.value:
            self.taxa = []
        else:
            raise ValueError("Incompatible arguments")

    @classmethod 
    def init_from_opts(cls, options, files=[]):
        if files:
            taxa = set(files[0].split(","))
            files = files[1:]
        else:
            taxa = []

        prune = cls(taxa, options.filename, options.attribute, options.value, options.inverse)
        return prune

    def process_tree(self, t):
        if self.taxa:
            # Pruning by a list of taxa
            if self.inverse:
                pruning_taxa = [l for l in t.get_leaves() if l.name in self.taxa]
            else:
                pruning_taxa = [l for l in t.get_leaves() if l.name not in self.taxa]
        else:
            # Pruning by an attribute value
            if self.inverse:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,self.attribute) and getattr(l,self.attribute) == self.value]
            else:
                pruning_taxa = [l for l in t.get_leaves() if hasattr(l,self.attribute) and getattr(l,self.attribute) != self.value]
        # Do the deed
        t.prune(pruning_taxa, preserve_branch_length=True)
        return t
