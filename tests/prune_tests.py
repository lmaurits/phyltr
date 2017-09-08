import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.prune import Prune
from phyltr.commands.annotate import Annotate

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

def test_file_prune():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    pruned = Prune(filename="tests/argfiles/taxa_abc.txt").consume(trees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert not any((x in leaves for x in ("A", "B", "C")))

def test_annotation_prune():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated = Annotate(filename="tests/argfiles/annotation.csv", key="taxon").consume(trees)
    pruned = Prune(attribute="f1", value="0").consume(annotated)
    for t in pruned:
        print(t.write())
        leaves = t.get_leaf_names()
        assert not any((x in leaves for x in ("A", "B", "C")))
