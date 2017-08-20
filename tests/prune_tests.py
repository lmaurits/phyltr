import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.prune import Prune

def test_prune():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    pruned = Prune(["A"]).consume(trees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert "A" not in leaves
        assert all((x in leaves for x in ("B", "C", "D", "E", "F")))

def test_inverse_prune():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    pruned = Prune(["A", "B"], inverse=True).consume(trees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("A", "B")))
        assert not any((x in leaves for x in ("C", "D", "E", "F")))

