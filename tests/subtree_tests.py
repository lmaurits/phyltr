import fileinput

from nose.tools import raises

from phyltr.plumbing.sources import NewickParser
from phyltr.main import build_pipeline
from phyltr.commands.subtree import Subtree

def test_init_from_args():
    subtree = Subtree.init_from_args("--file tests/argfiles/taxa_abc.txt")
    assert subtree.attribute == None
    assert subtree.filename == "tests/argfiles/taxa_abc.txt"
    assert subtree.value == None

    subtree = Subtree.init_from_args("--attribute foo --value bar")
    assert subtree.attribute == "foo"
    assert subtree.filename == None
    assert subtree.value == "bar"

@raises(ValueError)
def test_bad_init_no_args():
    Subtree()

@raises(ValueError)
def test_bad_init_no_attribute_only():
    Subtree(attribute="foo")

@raises(ValueError)
def test_bad_init_no_value_only():
    Subtree(value="bar")

@raises(ValueError)
def test_bad_init_empty_file():
    Subtree(filename="tests/argfiles/empty.txt")

def test_subtree():
    subtree = Subtree.init_from_args("A,B,C")
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subtrees = subtree.consume(trees)
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
        assert len(t.get_leaves()) == n
