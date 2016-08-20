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

import fileinput

import dendropy

from phyltr.utils.treestream_io import read_tree, write_tree
import phyltr.utils.phyoptparse as optparse

def read_rename_file(filename):

    """Read a file of names and their desired replacements and return a
    dictionary of this data."""

    rename = {}
    fp = open(filename, "r")
    for line in fp:
        old, new = line.strip().split(":")
        rename[old] = new
    fp.close()
    return rename

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--file', dest="filename",
                help='Specifies the translation file.')
    options, files = parser.parse_args()

    # Read translation file
    try:
        rename = read_rename_file(options.filename)
    except IOError:
        return 1

    # Read trees
    for line in fileinput.input(files):
        t = read_tree(line)
        # Rename nodes
        for node in t.seed_node.preorder_iter():
            if node.label in rename:
                node.label = rename[node.label]
            if node.taxon and node.taxon.label in rename:
                node.taxon.label = rename[node.taxon.label]

        # Output
        write_tree(t)

    # Done
    return 0
