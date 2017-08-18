"""Usage:
    phyltr prune taxa [<options>] [<files>]

Delete a specified set of nodes from the tree.

OPTIONS:

    taxa
        A comma-separated list of leaf taxon to delete from the tree

    -i, --inverse
        Specify an "inverse prune": delete all taxa *except* those given in
        the taxa option.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import sys

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Prune(PhyltrCommand):

    def __init__(self, taxa=None, filename=None, attribute=None, value=None, inverse=False):
        self.attribute = attribute
        self.filename = filename
        self.inverse = inverse
        self.value = value

        self.by_attribute = False

        if taxa:
            self.taxa = taxa
        elif filename:
            with open(options.filename, "r") as fp:
                self.taxa = [t.strip() for t in fp.readlines()]
            if not self.taxa:
                raise ValueError("Empty file!")
        elif self.attribute and self.value:
            self.taxa = []
        else:
            raise ValueError("Incompatible arguments")

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
        t.prune(pruning_taxa)
        return t

def run():

    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-i', '--inverse', action="store_true", default=False, dest="inverse")
    parser.add_option('-v', '--value', default=None)
    options, files = parser.parse_args()

    if (options.attribute and options.value) or options.filename:
        taxa = []
    else:
        if files:
            taxa = set(files[0].split(","))
            files = files[1:]
        else:
            sys.stderr.write("Must specify either a list of taxa, a file of taxa, or an attribute and value.\n")
            sys.exit(1)

    prune = Prune(taxa, options.filename, options.attribute, options.value, options.inverse)
    plumb(prune, files)
