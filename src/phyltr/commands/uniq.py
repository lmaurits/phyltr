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
    parser.add_option(
        '-l', '--lengths',
        action="store",
        dest="lengths",
        default="mean",
        help="|".join(valid_lengths))

    def __init__(self, cumulative=1.0, frequency=0.0, lengths="mean"):
        if lengths in self.valid_lengths:
            self.lengths = lengths
        else:
            raise ValueError("invalid --lengths option")
        self.cumulative = cumulative
        self.frequency = frequency
        self.topologies = {}
        self.N = 0

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(options.cumulative, options.frequency, options.lengths)

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
        for topology in topologies:
            equ_class = self.topologies[topology]
            top_freq = 1.0*len(equ_class) / self.N
            equ_class[0].support = top_freq
            cumulative += top_freq
            if top_freq < self.frequency:
                continue
            for nodes in zip(*[t.traverse() for t in equ_class]):
                dists = [n.dist for n in nodes]
                if self.lengths == "max":
                    dist = max(dists)
                elif self.lengths == "mean":
                    dist = sum(dists) / len(dists)
                elif self.lengths == "median":
                    dists.sort()
                    l = len(dists)
                    if l % 2 == 0:
                        dist = 0.5*(dists[l//2]+dists[l//2-1])
                    else:
                        dist = dists[l//2]
                elif self.lengths == "min":
                    dist = min(dists)
                nodes[0].dist = dist
            yield equ_class[0]
            if cumulative >= self.cumulative:
                return
