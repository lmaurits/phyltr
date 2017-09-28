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
from phyltr.plumbing.sources import ComplexNewickParser
from phyltr.plumbing.sinks import NewickFormatter
from phyltr.utils.phyltroptparse import OptionParser

class Cat(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr cat")
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)

    @classmethod 
    def init_from_opts(cls, options, files=[]):
        cat = Cat()
        return cat

    @classmethod
    def init_source(cls, options):
        return ComplexNewickParser(options.burnin, options.subsample)

    @classmethod
    def init_sink(cls, options, stream):
        return NewickFormatter(stream, annotations = not options.no_annotations)
    def process_tree(self, t):
        return t
