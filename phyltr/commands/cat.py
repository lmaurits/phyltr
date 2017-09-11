"""Usage:
    phyltr cat [<options>] [<files>]

Extract phylogenetic trees from the specified files and print them as a treestream.  The trees may contain trees formatted as a phyltr treestream or a NEXUS file.

OPTIONS:

    -b, --burnin
        Percentage of trees from each file to discard as "burnin".  Default is 0.
        
    -s, --subsample
        Frequency at which to subsample trees, i.e. "-s 10" will include
        only every 10th tree in the treestream.  Default is 1.
        
    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import ete3

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import complex_plumb

class Cat(PhyltrCommand):

    def __init__(self, burnin=0, subsample=1, annotations=True):
        self.burnin = burnin
        self.subsample = subsample
        self.annotations = annotations
        self.trees = []

    def process_tree(self, t):
        self.trees.append(t)

    def postprocess(self):
        burnin = int(round((self.burnin/100.0)*len(self.trees)))
        self.trees = self.trees[burnin::self.subsample]
        for t in self.trees:
            yield t

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)
    options, files = parser.parse_args()

    cat = Cat(options.burnin, options.subsample, not options.no_annotations)
    complex_plumb(cat, files)
