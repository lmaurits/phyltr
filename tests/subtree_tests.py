import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline
from phyltr.commands.subtree import Subtree

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
    subtrees = build_pipeline("annotate -f tests/argfiles/annotation.csv -k taxon | subtree --attribute f1 --value 0", trees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        print(t.write())
        assert len(t.get_leaves()) == n
