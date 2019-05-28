from phyltr.commands.base import PhyltrCommand
import phyltr.utils.cladeprob

class Support(PhyltrCommand):
    """
    Annotate a treestream with clade support probabilities, and optionally save
    clade support information to a file
    """
    __options__ = [
        (
            ('-a', '--age'),
            dict(
                action="store_true", dest="age", default=False,
                help="Whether or not to include clade age information (mean and 95%% HPD interval "
                     "in output)")),
        (
            ('-f', '--frequency'),
            dict(
                type=float, dest="frequency", default=0.0,
                help='Minimum clade frequency to include in output (by default all clades are '
                     'included)')),
        (
            ("-o", "--output"),
            dict(
                action="store", dest="filename", metavar="FILE",
                help="Filename to save a clade credibility report to")),
        (
            ('-s', '--sort'),
            dict(
                action="store_true", dest="sort", default=False,
                help='Reorder tree stream to print trees in order from highest to lowest product '
                     'of clade credibilities.')),
    ]
    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.trees = []
        self.cp = phyltr.utils.cladeprob.CladeProbabilities()

    def process_tree(self, t, _):
        self.trees.append(t)
        self.cp.add_tree(t)
        return None

    def postprocess(self, _):
        self.cp.compute_probabilities()

        # Save clade probabilities
        if self.opts.filename:
            self.cp.save_clade_report(self.opts.filename, self.opts.frequency, self.opts.age)

        # Annotate trees
        for t in self.trees:
            self.cp.annotate_tree(t)

        # Sort
        if self.opts.sort:
            trees = [(self.cp.get_tree_prob(t),t) for t in self.trees]
            trees.sort(key=lambda i: i[0])
            trees.reverse()
            self.trees = [t for (p,t) in trees]

        # Output
        for t in self.trees:
            yield t
