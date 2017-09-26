"""Usage:
    phyltr cat [<options>] [<files>]

Extract phylogenetic trees from the specified files and print them as a
treestream.  The trees may contain trees formatted as a phyltr treestream or a
NEXUS file.

OPTIONS:

    -b, --burnin
        Percentage of trees from each file to discard as "burn in".  Default is
        0, i.e. no burn in.
        
    -s, --subsample
        Frequency at which to subsample trees, i.e. "-s 10" will include
        only every 10th tree in the treestream.  Default is 1.
        
    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import os
import tempfile

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sources import NewickParser, ComplexNewickParser
from phyltr.utils.phyltroptparse import OptionParser

class Cat(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr cat")
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)

    def __init__(self, burnin=0, subsample=1, annotations=True):
        self.burnin = burnin
        self.subsample = subsample
        self.annotations = annotations
        self.n = 0
        self.temp_filename = None

    @classmethod 
    def init_from_opts(cls, options, files=[]):
        cat = Cat(options.burnin, options.subsample, not options.no_annotations)
        return cat

    @classmethod
    def init_source(cls, options):
        return ComplexNewickParser(options.burnin, options.subsample)

    def process_tree(self, t):
        return t

        # Skip the first self.burnin trees.
        # Note that self.burnin is converted from a percentage to an integer
        # count by self.preprocess()
        if self.n < self.burnin:
            self.n += 1
            return None

        res = t if self.n % self.subsample == 0 else None
        self.n += 1
        return res

    def preprocess(self):
        return

        # No pre-processing required if we aren't discarding burnin
        if self.burnin == 0:
            return
        # We want to know how many trees are coming in the stream.
        # So, let's rip through the stream, counting, and dump the trees to a
        # temp file (this way we don't eat a lot of memory holding them in RAM)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
            for t in self.stream:
                self.n += 1
                fp.write(t.write(features=[],format_root_node=True)+"\n")

        # Record how many trees we found and reset the counter for
        # self.consume()
        self.N = self.n
        self.n = 0

        # Convert burnin from a percentage to an integer count
        self.burnin = int(round((self.burnin/100.0)*self.N))

        # Replace the stream we just consumed with a fresh one which will
        # replay the same treestream.  We can use a regular NewickParser for
        # this, rather than doing NEXUS mangling etc. a second time.
        self.stream.close()
        self.temp_filename = fp.name
        self.new_fp = open(self.temp_filename, "r")
        self.stream = NewickParser().consume(self.new_fp.readlines())

    def postprocess(self):
        return []
        # Tidy up our temporary file
        if self.temp_filename:
            self.new_fp.close()
            os.unlink(self.temp_filename)
        return []
