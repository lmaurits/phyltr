"""Usage:
    phyltr dedupe [<options>] [<files>]

Remove duplicate taxa (i.e. taxa with the same name) from each tree in the
treestream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import random

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin

class Dedupe(PhyltrCommand):

    def process_tree(self, t):
        leaf_names = [l.name for l in t.get_leaves() if l.name]
        dupes = set([n for n in leaf_names if leaf_names.count(n) > 1])
        if not dupes:
            return t
        # Remove dupes one at a time
        victims = []
        for dupe in dupes:
            dupe_taxa = t.get_leaves_by_name(dupe)
            assert all([d.is_leaf() for d in dupe_taxa])
            # First try to collapse monophyletic dupes
            is_mono, junk, trash = t.check_monophyly([dupe],"name")
            if is_mono:
                mrca = t.get_common_ancestor(dupe_taxa)
                mrca.name = dupe
                for child in mrca.get_children():
                    child.detach()
            # If the dupe is non-monophyletic, kill at random
            else:
                victims.extend(random.sample(dupe_taxa,len(dupe_taxa)-1))
        if victims:
            t.prune([l for l in t.get_leaves() if l not in victims], preserve_branch_length=True)
#                for v in victims:
#                    v.detach()
        return t


def init_from_args(*args):
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args(*args)

    dedupe = Dedupe()
    return dedupe, files

def run():  # pragma: no cover
    dedupe, files = init_from_args()
    plumb_stdin(dedupe, files)

