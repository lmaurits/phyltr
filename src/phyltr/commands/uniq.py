import os

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.topouniq import are_same_topology
from phyltr.utils.phyltroptparse import VALID_LENGTHS, length_option

class Uniq(PhyltrCommand):
    """
    Merge all sets of trees with identical topologies in a tree stream into
    single trees.  The branch lengths of the merged trees are computed from those
    of all the trees with that topology.  Mean lengths are used by default.
    Trees are output in order of topology frequency, i.e. the first tree in the
    output stream summarises the most frequent topology.
    """
    __options__ = [
        (
            ('-c', '--cumulative'),
            dict(
                type=float, dest="cumulative", default=1.0,
                help='Cumulative topology frequency after which to stop output (by default '
                     'all topologies are included)')),
        (
            ('-f', '--frequency'),
            dict(
                type=float, dest="frequency", default=0.0,
                help='Minimum topology frequency to include in output (by default all '
                     'topologies are included)')),
        length_option("Specifies the method used to compute branch lengths when trees with "
                      "identical topologies are merged."),
        (
            ('-s', '--separate'),
            dict(
                action="store_true", dest="separate", default=False,
                help="Write all trees in the input tree stream into files grouping them by "
                     "topology, resulting in one file per topology.  Still passes all trees to "
                     "stdout as per usual.  Note that unless used in conjunction with an option "
                     "such as --frequency which limits how many topologies are to be passed, this "
                     "may result in hundreds or thousands of small files being created! Files are "
                     "named `phyltr_uniq_$n.trees`, where $n is an integer index beginning from 1. "
                     "phyltr_uniq_1.trees contains all trees having the most frequent topology, "
                     "for example. Existing files will be silently overwritten, users are "
                     "responsible for organising the results of consecutive runs.")),
        (
            ('-o', '--output'),
            dict(
                default='.',
                help="If --separate is set, output files are written to this directory")),
    ]

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.topologies = {}

    def process_tree(self, t, _):
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        for exemplar in self.topologies:
            if are_same_topology(t, exemplar):
                self.topologies[exemplar].append(t)
                break
        else:
            self.topologies[t] = [t]
        return None
       
    def postprocess(self, tree_count):
        # Order topologies by descending frequency
        cumulative = 0.0
        for n, (_, equ_class) in enumerate(
                sorted(self.topologies.items(), key=lambda x: -len(x[1]))):
            representative = equ_class[0]   # This tree will be annotated and yielded
            # Compute topoogy frequency
            top_freq = 1.0*len(equ_class) / tree_count
            if top_freq < self.opts.frequency:
                continue
            cumulative += top_freq
            if self.opts.separate:
                # Save all pristine trees to file before annotating a representative
                with open(
                        os.path.join(self.opts.output, "phyltr_uniq_%d.trees" % (n+1)), "w") as fp:
                    fp.write(''.join([t.write() + "\n" for t in equ_class]))
            # Begin annotating rep
            representative.support = top_freq
            # Compute root height stats
            heights = sorted([t.get_farthest_leaf()[1] for t in equ_class])
            lower, median, upper = [heights[int(x*len(heights))] for x in (0.025, 0.5, 0.975)]
            representative.add_feature("age_mean", "%.2f" % (sum(heights)/len(heights)))
            representative.add_feature("age_median", "%.2f" % median)
            representative.add_feature("age_95_HPD", "{%.2f-%.2f}" % (lower, upper))
            # Set branch distances
            for nodes in zip(*[t.traverse() for t in equ_class]):
                nodes[0].dist = VALID_LENGTHS[self.opts.lengths]([n.dist for n in nodes])
            yield representative
            if cumulative >= self.opts.cumulative:
                return
