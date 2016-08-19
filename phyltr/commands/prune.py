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

import fileinput
import sys

import dendropy

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-i', '--inverse', action="store_true", default=False, dest="inverse")
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
        if options.inverse:
            t.retain_taxa_with_labels(taxa)
        else:
            t.prune_taxa_with_labels(taxa)
        print t.as_string(schema="newick", suppress_rooting=True,suppress_annotations=False).strip()

    # Done
    return 0
