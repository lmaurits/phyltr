"""Usage:
    phyltr clades [<options>] [<files>]

Produce a list showing all clades in a treestream and the proportion of trees
in the stream which contain each clade.  The format of the output is
identical to that produced by the 'phyltr support' command when using the
'-o' option, and some of the same options are available.

OPTIONS:

    -f, --frequency
        Minimum clade frequency to include in output (default 0.0, i.e. all
        clades are included)

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import dendropy

import phyltr.utils.phyoptparse as optparse
import phyltr.utils.cladeprob

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-f', '--frequency', type="float", dest="threshold",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    trees = []
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input(files):
        t = dendropy.Tree.get_from_string(line,schema="newick")
        cp.add_tree(t)
    cp.compute_probabilities()

    # Output
    cp.save_clade_report("/dev/stdout", options.threshold)

    # Done
    return 0
