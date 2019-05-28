from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sources import ComplexNewickParser
from phyltr.plumbing.sinks import NewickFormatter


class Cat(PhyltrCommand):
    """Extract phylogenetic trees from the specified files and print them as a treestream.
The trees may contain trees formatted as a phyltr treestream or a NEXUS file.
    """
    __options__ = [
        (
            ('-b', '--burnin'),
            dict(
                action="store", dest="burnin", type=int, default=0,
                help="Percentage of trees from each file to discard as 'burn in'.  Default is 0, "
                     "i.e. no burn in.")),
        (
            ('-s', '--subsample'),
            dict(
                action="store", dest="subsample", type=int, default=1,
                help="Frequency at which to subsample trees, i.e. '-s 10' will include only every "
                     "10th tree in the treestream.  Default is 1.")),
        (
            ('--no-annotations',),
            dict(
                action="store_true", dest="no_annotations", default=False,
                help="Do not include any annotations on nodes (e.g. clock rates, phylogeographic "
                     "locations, etc.), print only standard metadata (i.e. branch lengths and "
                     "clade supports)")),
        (
            ('--topology-only',),
            dict(
                action="store_true", dest="topology_only", default=False,
                help="Print very clean trees with only the leaf names and branching structure "
                     "included, removing branch lengths, clade supports and any other annotations. "
                     "Stronger than, and overrides, --no-annotations.")),
    ]

    def init_source(self):
        return ComplexNewickParser(self.opts.burnin, self.opts.subsample)

    def init_sink(self, stream):
        return NewickFormatter(
            stream, annotations=not self.opts.no_annotations, topology_only=self.opts.topology_only)

    def process_tree(self, t):
        return t
