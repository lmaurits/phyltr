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

import phyltr.utils.phyoptparse as optparse
import phyltr.utils.cladeprob
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin

class Clades(PhyltrCommand):
    
    def __init__(self, frequency=0.0, ages=False):
        self.frequency = frequency
        self.ages = ages
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t):
        self.cp.add_tree(t)

    def postprocess(self):
        self.cp.compute_probabilities()
        self.cp.save_clade_report("/dev/stdout", self.frequency, self.ages)
        return []


def init_from_args(*args):
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--ages', action="store_true", dest="age", default=False, help="Include age information in report.")
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=1.0, help='Minimum clade frequency to report.')
    options, files = parser.parse_args(*args)
    clades = Clades(options.frequency, options.age)
    return clades, files

def run():
    clades, files = init_from_args()
    plumb_stdin(clades, files)

