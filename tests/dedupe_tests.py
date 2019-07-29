from phyltr.commands.dedupe import Dedupe

def test_dedupe(treefilenewick):
    trees = list(treefilenewick('duplicate_taxa.trees'))
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

def test_monophyletic_dedupe(treefilenewick):
    trees = list(treefilenewick('monophyletic_dupe_taxa.trees'))
    for t in trees:
        leaves = t.get_leaf_names()
        assert any(leaves.count(x) != 1  for x in ("A", "B", "C", "D", "E", "F"))
    deduped = Dedupe().consume(trees)
    for t in deduped:
        leaves = t.get_leaf_names()
        assert all((leaves.count(x) == 1  for x in ("A", "B", "C", "D", "E", "F")))
