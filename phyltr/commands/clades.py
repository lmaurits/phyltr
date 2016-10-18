"""Usage:
    phyltr clades [<options>] [<files>]

Produce a list showing all clades in a treestream and the proportion of trees
in the stream which contain each clade.  The format of the output is
identical to that produced by the 'phyltr support' command when using the
'-o' option, and some of the same options are available.

OPTIONS:

    -a, --ages
        Whether or not to include clade age information (mean and 95% HPD
        interval in output)
    -f, --frequency
        Minimum clade frequency to include in output (default 0.0, i.e. all
        clades are included)

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import ete2

import phyltr.utils.phyoptparse as optparse
import phyltr.utils.cladeprob

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--ages', action="store_true", dest="age", default=False, help="Include age information in report.")
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args()

    # Read trees and compute clade probabilities
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        cp.add_tree(t)
    cp.compute_probabilities()

    # Output
    cp.save_clade_report("/dev/stdout", options.frequency, options.age)

    # Done
    return 0
