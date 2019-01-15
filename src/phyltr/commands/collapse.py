"""Usage:
    phyltr collapse [<options>] [<files>]

Collapse monophyletic sets of leaf nodes, by turning their MRCA into a leaf,
and giving the newly formed leaf a specified label.

OPTIONS:

    -a, --attribute
        Specify an attribute by which to collapse clades instead of a
        translation file.  Clades will only be collapsed for attribute values
        which are monophyletic.

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
from collections import defaultdict

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class MonophylyFailure(Exception):
    """Raised when asked to collapse a non monophyletic taxon set."""

class Collapse(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr collapse")
    parser.add_option('-a', '--attribute', dest="attribute", default=None)
    parser.add_option('-t', '--translate',
                help='Specifies the translation file.',default=None)

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls({}, options.translate, options.attribute)

    def __init__(self, clades=None, filename=None, attribute=None):
        if clades:
            self.trans = clades # trans = translation
        elif filename:
            self.filename = filename
            self.read_clade_file(self.filename)
        elif attribute:
            self.attribute = attribute
            self.trans = {}
        else:
            raise ValueError("Must provide a dictionary of clades, a filename or an attribute.")

    def process_tree(self, t):
        if self.trans:
            self.collapse_by_dict(t)
        else:
            self.collapse_by_attribute(t)
        return t

    def read_clade_file(self, filename):

        """Read a file of names and clade definitions and return a dictionary of
        this data."""

        self.trans = {}
        with open(filename, "r") as fp:
            for line in fp:
                name, clade = line.strip().split(":")
                clade = clade.strip().split(",")
                self.trans[name] = clade

    def collapse_by_dict(self, t):
        cache = t.get_cached_content()
        tree_leaves = cache[t]
        for name, clade in self.trans.items():
            # Get a list of leaves in this tree
            clade_leaves = [l for l in tree_leaves if l.name in clade]
            if not clade_leaves:
                continue
            try:
                self.test_monophyly_and_collapse(t, cache, name, clade_leaves)
            except MonophylyFailure:
                # Clade is not monophyletic.  We can't collapse it.
                sys.stderr.write("Monophyly failure for clade: %s\n" % name)
#                sys.stderr.write("Interlopers: %s\n" % ",".join([n.name for n in set(mrca_leaves) - set(clade_leaves)]))
                return 1

    def collapse_by_attribute(self, t):
        cache = t.get_cached_content()
        tree_leaves = cache[t]
        # Build a dictionary mapping attribute values to lists of leaves
        values = defaultdict(list)
        for leaf in tree_leaves:
            if hasattr(leaf, self.attribute):
                values[getattr(leaf, self.attribute)].append(leaf)
        # Do monophyly tests
        for value, clade_leaves in values.items():
            try:
                self.test_monophyly_and_collapse(t, cache, value, clade_leaves)
            except MonophylyFailure:
                # Clade is not monophyletic.  We can't collapse it.
                sys.stderr.write("Monophyly failure for attribute value: %s=%s\n" % (self.attribute, value))

    def test_monophyly_and_collapse(self, t, cache, clade, clade_leaves):
        # Check monophyly
        if len(clade_leaves) == 1:
            mrca = clade_leaves[0]  # .get_common_ancestor works oddly for singletons
        else:
            mrca = t.get_common_ancestor(clade_leaves)
        mrca_leaves = cache[mrca]
        if set(mrca_leaves) != set(clade_leaves):
            raise MonophylyFailure

        # Clade is monophyletic, so rename and prune
        # But don't mess up distances
        mrca.name = clade
        leaf, dist = mrca.get_farthest_leaf()
        mrca.dist += dist
        for child in mrca.get_children():
            child.detach()
