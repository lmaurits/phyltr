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

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import complex_plumb

class Cat(PhyltrCommand):

    def __init__(self, burnin=0, subsample=1, annotations=True):
        self.burnin = burnin
        self.subsample = subsample
        self.annotations = annotations
        self.trees = []
        self.n = 0

    def process_tree(self, t):
        if self.burnin:
            # If we're discarding a fixed percentage as burn-in, we need to
            # know the total number of trees.  So for now, just dump 'em in
            # a list, consume ALL the memory...
            self.trees.append(t)
            return None
        else:
            # Otherwise, we can subsample as we go
            if self.n % self.subsample == 0:
                self.n += 1
                return t
            else:
                self.n += 1 # Would be nice to avoid duplicating this
                return None

    def postprocess(self):
        if self.burnin:
            # If there's a burn-in, we now have all trees sitting in a list,
            # so dump 'em all now
            burnin = int(round((self.burnin/100.0)*len(self.trees)))
            self.trees = self.trees[burnin::self.subsample]
            for t in self.trees:
                yield t
        else:
            # If there's no burn-in, we've already done everything
            raise StopIteration

def init_from_args(*args):

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)
    options, files = parser.parse_args(*args)

    cat = Cat(options.burnin, options.subsample, not options.no_annotations)
    return cat, files

def run():  # pragma: no cover
    cat, files = init_from_args()
    complex_plumb(cat, files)
