"""Usage:
    phyltr nexus [<files>]

Convert a treestream to a file in the NEXUS forma.  The NEXUS output is printed to stdout, where it can be redirected to a file.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import dendropy

from phyltr.utils.treestream_io import read_tree, write_tree
import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    treelist = dendropy.TreeList()
    # Read trees
    first = True
    for count, line in enumerate(fileinput.input(files),1):
        t = read_tree(line)
        treelist.append(t)

    print treelist.as_string(schema="nexus", suppress_rooting=True, suppress_annotations=False, translate_tree_taxa=True)
    return 0
