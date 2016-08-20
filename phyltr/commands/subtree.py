"""Usage:
    phyltr subtree taxa [<options>] [<files>]

Replace each tree with the minimal subtree containing the specified taxa.

OPTIONS:

    taxa
        A comma-separated list of leaf taxa to keep in the tree

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import sys

import dendropy

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    if files:
        taxa = set(files[0].split(","))
        files = files[1:]
    else:
        # Improper usage
        sys.stderr.write("Must specify a list of taxa.\n")
        sys.exit(1)

    first = True
    for line in fileinput.input(files):
        t = dendropy.Tree.get_from_string(line,schema="newick",rooting="default-rooted")
        t.seed_node = t.mrca(taxon_labels=taxa)
        print t.as_string(schema="newick", suppress_rooting=True).strip()

    # Done
    return 0
