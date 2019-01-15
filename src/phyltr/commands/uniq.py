"""Usage:
    phyltr uniq [<options>] [<files>]

Merge all sets of trees with identical topologies in a tree stream into
single trees.  The branch lengths of the merged trees are computed from those
of all the trees with that topology.  Mean lengths are used by default.

OPTIONS:

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
    parser.add_option(
        '-l', '--lengths',
        action="store",
        dest="lengths",
        default="mean",
        help="|".join(valid_lengths))

    def __init__(self, lengths="mean"):
        if lengths in self.valid_lengths:
            self.lengths = lengths
        else:
            raise ValueError("invalid --lengths option")

        self.topologies = {}
        self.ordered_exemplars = []

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(options.lengths)

    def process_tree(self, t):
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        for exemplar in self.topologies:
            if are_same_topology(t, exemplar):
                self.topologies[exemplar].append(t)
                break
        else:
            self.topologies[t] = [t]
            self.ordered_exemplars.append(t)

        return None
       
    def postprocess(self):
        for exemplar in self.ordered_exemplars:
            equ_class = self.topologies[exemplar]
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
