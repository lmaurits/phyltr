"""Usage:
    phyltr cat [<options>] [<files>]

Extract phylogenetic trees from the specified files and print them as a
treestream.  The trees may contain trees formatted as a phyltr treestream or a
NEXUS file.

OPTIONS:

    -b, --burnin
        Percentage of trees from each file to discard as "burn in".  Default is
        0, i.e. no burn in.

    --no-annotations
        Do not include any annotations on nodes (e.g. clock rates, phylogeographic
        locations, etc.), print only standard metadata (i.e. branch lengths and
        clade supports)
        
    -s, --subsample
        Frequency at which to subsample trees, i.e. "-s 10" will include
        only every 10th tree in the treestream.  Default is 1.

    --topology-only
        Print very clean trees with only the leaf names and branching structure
        included, removing branch lengths, clade supports and any other annotations.
        Stronger than, and overrides, --no-annotations.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sources import ComplexNewickParser
from phyltr.plumbing.sinks import NewickFormatter
from phyltr.utils.phyltroptparse import OptionParser


class Cat(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr cat")
    parser.add_option('-b', '--burnin', action="store", dest="burnin", type="int", default=0)
    parser.add_option('-s', '--subsample', action="store", dest="subsample", type="int", default=1)
    parser.add_option('--no-annotations', action="store_true", dest="no_annotations", default=False)
    parser.add_option('--topology-only', action="store_true", dest="topology_only", default=False)

    def __init__(self, burnin=0, subsample=1, annotations=True, topology_only=False):
        self.burnin = burnin
        self.subsample = subsample
        self.annotations = annotations
        self.topology_only = topology_only

    @classmethod 
    def init_from_opts(cls, options, files=None):
        return cls(options.burnin, options.subsample, annotations = not options.no_annotations, topology_only = options.topology_only)

    def init_source(self):
        return ComplexNewickParser(self.burnin, self.subsample)

    def init_sink(self, stream):
        return NewickFormatter(stream, annotations = self.annotations, topology_only = self.topology_only)

    def process_tree(self, t):
        return t
