from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter
import phyltr.utils.cladeprob

class Clades(PhyltrCommand):
    """
    Produce a list showing all clades in a treestream and the proportion of trees
    in the stream which contain each clade.  The format of the output is
    identical to that produced by the 'phyltr support' command when using the
    '-o' option, and some of the same options are available.
    """
    __options__ = [
        (
            ('-a', '--ages'),
            dict(
                action="store_true", dest="ages", default=False,
                help="Whether or not to include clade age information (mean and 95%% HPD interval "
                     "in output)")),
        (
            ('-f', '--frequency'),
            dict(
                type=float, dest="frequency", default=0.0,
                help='Minimum clade frequency to include in output (default 0.0, i.e. all clades '
                     'are included)')),
    ]

    sink = StringFormatter

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t, _):
        self.cp.add_tree(t)

    def postprocess(self, _):
        self.cp.compute_probabilities()
        self.cp.save_clade_report("/dev/stdout", self.opts.frequency, self.opts.ages)
        return []
