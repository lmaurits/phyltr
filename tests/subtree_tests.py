import fileinput
import shlex

from nose.tools import raises

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline
from phyltr.commands.subtree import Subtree, init_from_args

def test_init_from_args():
    subtree, files = init_from_args(shlex.split("--file tests/argfiles/taxa_abc.txt"))
    assert subtree.attribute == None
    assert subtree.filename == "tests/argfiles/taxa_abc.txt"
    assert subtree.value == None

    subtree, files = init_from_args(shlex.split("--attribute foo --value bar"))
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
