"""Usage:
    phyltr support [<options>] [<files>]

Annotate a treestream with clade support probabilities, and optionally save clade support information to a file

OPTIONS:

    -a, --ages
        Whether or not to include clade age information (mean and 95% HPD
        interval in output)

    -s, --sort
        Reorder tree stream to print trees in order from highest to lowest
        product of clade credibilities.

    -o, --output
        Filename to save a clade credibility report to

    -f, --frequency
        Minimum clade frequency to include in output (default 0.0, i.e. all
        clades are included)

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin
import phyltr.utils.cladeprob

class Support(PhyltrCommand):
   
    def __init__(self, frequency=0.0, ages=False, sort=False, filename=None):
        self.frequency = frequency
        self.ages = ages
        self.sort = sort
        self.filename = filename
        self.trees = []
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t):
        self.trees.append(t)
        self.cp.add_tree(t)
        return None

    def postprocess(self):
        self.cp.compute_probabilities()

        # Save clade probabilities
        if self.filename:
            self.cp.save_clade_report(self.filename, self.frequency, self.ages)

        # Annotate trees
        for t in self.trees:
            self.cp.annotate_tree(t)

        # Sort
        if self.sort:
            trees = [(self.cp.get_tree_prob(t),t) for t in self.trees]
            trees.sort()
            trees.reverse()
            self.trees = [t for (p,t) in trees]

        # Output
        for t in self.trees:
            yield t


def init_from_args(*args):
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--age', action="store_true", dest="age", default=False, help="Include age information in report.")
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=0.0, help='Minimum clade frequency to report.')
    parser.add_option("-o", "--output", action="store", dest="filename",
        help="save clades to FILE", metavar="FILE")
    parser.add_option('-s', '--sort', action="store_true", dest="sort", default=False)
    options, files = parser.parse_args(*args)

    support = Support(options.frequency, options.age, options.sort, options.filename)
    return support, files

def run():  # pragma: no cover
    support, files = init_from_args()
    plumb_stdin(support, files)
