"""Usage:
    phyltr collapse [<options>] [<files>]

Collapse monophyletic sets of leaf nodes, by turning their MRCA into a leaf,
and giving the newly formed leaf a specified label.

OPTIONS:

    -t, --translate
        The filename of the translate file.  Each line of the translate file
        should be of the format:
            "label:taxa1,taxa2,taxa3,...."
        The MRCA of the specified taxa will be replaced by a leaf named
        "label".

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import sys

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Collapse(PhyltrCommand):

    def __init__(self, filename=None, attribute=None):
        self.filename = filename
        self.attribute = attribute

        args = (filename, attribute)
        if all(args) or not any(args):
            raise ValueError("Provide a filename or an attribute, but not both.")
        
        if filename:
            self.read_clade_file(self.fliename)

    def process_tree(self, t):
        if self.filename:
            self.collapse_from_file(t)
        else:
            self.collapse_by_attribute(t)
        return t

    def read_clade_file(filename):

        """Read a file of names and clade definitions and return a dictionary of
        this data."""

        self.trans = []
        fp = open(filename, "r")
        for line in fp:
            name, clade = line.strip().split(":")
            clade = clade.strip().split(",")
            self.trans.append((clade, name))
        fp.close()

    def collapse_from_file(self, t):
        cache = t.get_cached_content()
        tree_leaves = cache[t]
        for clade, name in self.trans:
            # Get a list of leaves in this tree
            clade_leaves = [l for l in tree_leaves if l.name in clade]
            if not clade_leaves:
                continue
            # Check monophyly
            if len(clade_leaves) == 1:
                mrca = clade_leaves[0]  # .get_common_ancestor works oddly for singletons
            else:
                mrca = t.get_common_ancestor(clade_leaves)
            mrca_leaves = cache[mrca]
            if set(mrca_leaves) == set(clade_leaves):
                # Clade is monophyletic, so rename and prune
                # But don't mess up distances
                mrca.name = name
                leaf, dist = mrca.get_farthest_leaf()
                mrca.dist += dist
                for child in mrca.get_children():
                    child.detach()
            else:
                # Clade is not monophyletic.  We can't collapse it.
                sys.stderr.write("Monophyly failure for clade: %s\n" % name)
                sys.stderr.write("Interlopers: %s\n" % ",".join([n.name for n in set(mrca_leaves) - set(clade_leaves)]))
                return 1

    def collapse_by_attribute(self, t):
        values = set([getattr(n,self.attribute) for n in t.traverse() if hasattr(n,self.attribute)])
        if not t.check_monophyly(values, self.attribute, ignore_missing=True):
            sys.stderr.write("Monophyly failure for attribute: %s" % self.attribute)
            return 1

        for v in values:
            mrca = list(t.get_monophyletic([v], self.attribute))[0]
            mrca.name = v
            mrca.add_feature(self.attribute, v)
            leaf, dist = mrca.get_farthest_leaf()
            mrca.dist += dist
            for child in mrca.get_children():
                child.detach()

def run():

    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', dest="attribute", default=None)
    parser.add_option('-t', '--translate',
                help='Specifies the translation file.',default=None)
    options, files = parser.parse_args()

    collapse = Collapse(options.translate, options.attribute)
    plumb(collapse, files)
