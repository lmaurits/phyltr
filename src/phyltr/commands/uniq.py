"""Usage:
    phyltr uniq [<options>] [<files>]

Merge all sets of trees with identical topologies in a tree stream into
single trees.  The branch lengths of the merged trees are computed from those
of all the trees with that topology.  Mean lengths are used by default.
Trees are output in order of topology frequency, i.e. the first tree in the
output stream summarises the most frequent topology.

OPTIONS:

    -c, --cumulative
        Cumulative topology frequency after which to stop output (default 1.0,
        i.e. all topologies are included)

    -f, --frequency
        Minimum topology frequency to include in output (default 0.0, i.e. all
        topologies are included)

    -l, --length
        Specifies the method used to compute branch lengths when trees with
        identical topologies are merged.  Must be one of: "max", "mean",
        "median", or "min".  Default is mean.

    -s, --separate
        Write all trees in the input tree stream into files grouping them by
        topology, resulting in one file per topology.  Still passes all trees
        to stdout as per usual.  Note that unless used in conjunction with an
        option such as --frequency which limits how many topologies are to be
        passed, this may result in hundreds or thousands of small files being
        created!  Files are named `phyltr_uniq_$n.trees`, where $n is an
        integer index beginning from 1.  phyltr_uniq_1.trees contains all trees
        having the most frequent topology, for example.  Existing files will
        be silently overwritten, users are responsible for organising the
        results of consecutive runs.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from six.moves import zip

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser
from phyltr.utils.topouniq import are_same_topology

class Uniq(PhyltrCommand):

    valid_lengths = ["max", "mean", "median", "min"]
    parser = OptionParser(__doc__, prog="phyltr uniq")
    parser.add_option('-c', '--cumulative', type="float", dest="cumulative",
            default=1.0, help='Cumulative topology frequency to report.')
    parser.add_option('-f', '--frequency', type="float", dest="frequency",
            default=0.0, help='Minimum topology frequency to report.')
    parser.add_option('-l', '--lengths', action="store", dest="lengths",
            default="mean", help="|".join(valid_lengths))
    parser.add_option('-s', '--separate', action="store_true", dest="separate",
            default=False, help="Separate trees into per-topology files.")

    def __init__(self, cumulative=1.0, frequency=0.0, lengths="mean", separate=False):
        if lengths in self.valid_lengths:
            self.lengths = lengths
        else:
            raise ValueError("invalid --lengths option")
        self.cumulative = cumulative
        self.frequency = frequency
        self.separate = separate
        self.topologies = {}
        self.N = 0

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(options.cumulative, options.frequency, options.lengths,
                options.separate)

    def process_tree(self, t):
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        for exemplar in self.topologies:
            if are_same_topology(t, exemplar):
                self.topologies[exemplar].append(t)
                break
        else:
            self.topologies[t] = [t]
        self.N += 1
        return None
       
    def postprocess(self):
        # Order topologies by frequency
        topologies = [(len(v), k) for k,v in self.topologies.items()]
        topologies.sort(reverse=True, key=lambda x: x[0])
        topologies = (t for (n,t) in topologies)
        cumulative = 0.0
        for n, topology in enumerate(topologies):
            equ_class = self.topologies[topology]
            representative = equ_class[0]   # This tree will be annotated and yielded
            # Compute topoogy frequency
            top_freq = 1.0*len(equ_class) / self.N
            if top_freq < self.frequency:
                continue
            cumulative += top_freq
            if self.separate:
                # Save all pristine trees to file before annotating a representative
                with open("phyltr_uniq_%d.trees" % (n+1), "w") as fp:
                    for t in equ_class:
                        fp.write(t.write()+"\n")
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
                dists = [n.dist for n in nodes]
                if self.lengths == "max":
                    dist = max(dists)
                elif self.lengths == "min":
                    dist = min(dists)
                elif self.lengths == "mean":
                    dist = sum(dists) / len(dists)
                elif self.lengths == "median":
                    dists.sort()
                    l = len(dists)
                    if l % 2 == 0:
                        dist = 0.5*(dists[l//2]+dists[l//2-1])
                    else:
                        dist = dists[l//2]
                nodes[0].dist = dist
            yield representative
            if cumulative >= self.cumulative:
                return
