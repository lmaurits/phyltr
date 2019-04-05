"""Usage:
    phyltr rename [<options>] [<files>]

Rename the nodes in a treestream.  The mapping from old to new names is read
from a file.

OPTIONS:

    -f, --file
        The filename of the translation file.  Each line of the translate
        file should be of the format:
            "old:new"

    -r, --remove-missing
        If there are taxa in the tree which are not in the translation file,
        remove them (in the manner of subtree, not prune)

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class Rename(PhyltrCommand):
    
    parser = OptionParser(__doc__, prog="phyltr rename")
    parser.add_option('-f', '--file', dest="filename",
                help='Specifies the translation file.')
    parser.add_option('-r', '--remove-missing', dest="remove",action="store_true",
            default=False,
                help='Remove untranslated taxa.')

    def __init__(self, rename=None, filename=None, remove=False):
        if rename:
            self.rename = rename
        elif filename:
            self.read_rename_file(filename)
        else:
            raise ValueError("Must supply renaming dictionary or filename!")
        self.remove = remove

        self.first = True

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(filename=options.filename, remove=options.remove)

    def read_rename_file(self, filename):

        """Read a file of names and their desired replacements and return a
        dictionary of this data."""

        rename = {}
        with open(filename, "r") as fp:
            for line in fp:
                old, new = line.strip().split(":")
                old = ",".join((x.strip() for x in old.split(",")))
                new = new.strip()
                rename[old] = new
            fp.close()
        self.rename = rename

    def process_tree(self, t):
        # Rename nodes
        for node in t.traverse():
            node.name = self.rename.get(node.name,
                    "KILL-THIS-NODE" if self.remove else node.name)

        keepers = [l for l in t.get_leaves() if l.name != "KILL-THIS-NODE"]
        if self.first:
            n_leaves = len(t.get_leaves())
            self.pruning_needed = len(keepers) < n_leaves
            self.first = False

        if self.pruning_needed:
            mrca = t.get_common_ancestor(keepers)
            if t != mrca:
                t = mrca
            t.prune(keepers, preserve_branch_length=True)

        return t
