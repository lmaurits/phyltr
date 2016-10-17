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

import fileinput
import random
import sys

import ete2

import phyltr.utils.phyoptparse as optparse

def run():

    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    for line in fileinput.input(files):
        t = ete2.Tree(line)
        leaf_names = [l.name for l in t.get_leaves() if l.name]
        dupes = set([n for n in leaf_names if leaf_names.count(n) > 1])
        if not dupes:
            print t.write(features=[],format_root_node=True)
            continue
        # Remove dupes one at a time
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
                victims = random.sample(dupe_taxa,len(dupe_taxa)-1)
                t.prune([l for l in t.get_leaves() if l not in victims])
#                for v in victims:
#                    v.detach()
        print t.write(features=[],format_root_node=True)

    # Done
    return 0
