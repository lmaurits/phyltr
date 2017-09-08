import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.subtree import Subtree
from phyltr.commands.annotate import Annotate

def test_subtree():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subtrees = Subtree(["A","B","C"]).consume(trees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        assert len(t.get_leaves()) == n

def test_file_subtree():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subtrees = Subtree(filename="tests/argfiles/taxa_abc.txt").consume(trees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        assert len(t.get_leaves()) == n

def test_annotation_subtree():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated = Annotate(filename="tests/argfiles/annotation.csv", key="taxon").consume(trees)
    subtrees = Subtree(attribute="f1", value="0").consume(annotated)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        print(t.write())
        assert len(t.get_leaves()) == n
