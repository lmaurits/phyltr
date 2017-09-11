import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.dedupe import Dedupe

def test_dedupe():
    lines = fileinput.input("tests/treefiles/duplicate_taxa.trees")
    trees = list(NewickParser().consume(lines))
    for t in trees:
        orig_leaves = t.get_leaf_names()
        assert len(orig_leaves) == 6
        assert orig_leaves.count("A") == 2
        assert all((orig_leaves.count(x) == 1  for x in ("B", "C", "E", "F")))
    deduped = Dedupe().consume(trees)
    for t in deduped:
        leaves = t.get_leaf_names()
        assert len(leaves) == 5
        assert all((leaves.count(x) == 1  for x in ("A", "B", "C", "E", "F")))
