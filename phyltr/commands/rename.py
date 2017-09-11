"""Usage:
    phyltr rename [<options>] [<files>]

Rename the nodes in a treestream.  The mapping from old to new names is read from a file.

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

import sys

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin

class Rename(PhyltrCommand):
    
    def __init__(self, rename=None, filename=None, remove=False):
        if rename:
            self.rename = rename
        elif filename:
            self.read_rename_file(filename)
        else:
            raise ValueError("Must supply renaming dictionary or filename!")
        self.remove = remove

        self.first = True

    def read_rename_file(self, filename):

        """Read a file of names and their desired replacements and return a
        dictionary of this data."""

        rename = {}
        with open(filename, "r") as fp:
            for line in fp:
                old, new = line.strip().split(":")
                rename[old.strip()] = new.strip()
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

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--file', dest="filename",
                help='Specifies the translation file.')
    parser.add_option('-r', '--remove-missing', dest="remove",action="store_true",
                help='Remove untranslated taxa.')
    options, files = parser.parse_args()

    rename = Rename(filename=options.filename, remove=options.remove)
    plumb_stdin(rename, files)

