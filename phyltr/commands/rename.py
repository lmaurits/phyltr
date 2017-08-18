"""Usage:
    phyltr rename [<options>] [<files>]

Rename the nodes in a treestream.  The mapping from old to new names is read from a file.

OPTIONS:

    -f, --file
        The filename of the translation file.  Each line of the translate
        file should be of the format:
            "old:new"

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import sys

from phyltr.commands.generic import PhyltrCommand, plumb

import phyltr.utils.phyoptparse as optparse

class Rename(PhyltrCommand):
    
    def __init__(self, filename):
        self.read_rename_file(filename)

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
            if node.name in self.rename:
                node.name = self.rename[node.name]
        return t

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--file', dest="filename", help='Specifies the translation file.')
    print(sys.argv)
    options, files = parser.parse_args()

    rename = Rename(options.filename)
    plumb(rename, files)
