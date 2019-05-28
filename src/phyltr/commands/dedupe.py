import random
import collections

from phyltr.commands.base import PhyltrCommand

class Dedupe(PhyltrCommand):
    """
    Remove duplicate taxa (i.e. taxa with the same name) from each tree in the
    treestream.
    """
    def process_tree(self, t, _):
        leaf_names = collections.Counter([l.name for l in t.get_leaves() if l.name])
        # Remove dupes one at a time
        victims = []
        for leaf_name, count in leaf_names.most_common():
            if count == 1:  # leaf name only occurs once.
                break
            dupe_taxa = t.get_leaves_by_name(leaf_name)
            assert all([d.is_leaf() for d in dupe_taxa])
            # First try to collapse monophyletic dupes
            is_mono, junk, trash = t.check_monophyly([leaf_name],"name")
            if is_mono:
                mrca = t.get_common_ancestor(dupe_taxa)
                mrca.name = leaf_name
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
