import fileinput

import pytest

from phyltr.plumbing.sources import NewickParser
from phyltr.main import build_pipeline
from phyltr.commands.subtree import Subtree

def test_init_from_args():
    subtree = Subtree.init_from_args("--file tests/argfiles/taxa_abc.txt")
    assert subtree.attribute == None
    assert subtree.filename == "tests/argfiles/taxa_abc.txt"
    assert subtree.values == None

    subtree = Subtree.init_from_args("--attribute foo --values bar")
    print(subtree.values)
    assert subtree.attribute == "foo"
    assert subtree.filename == None
    assert subtree.values == ["bar"]

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Subtree()

def test_bad_init_no_attribute_only():
    with pytest.raises(ValueError):
        Subtree(attribute="foo")

def test_bad_init_no_value_only():
    with pytest.raises(ValueError):
        Subtree(value="bar")

def test_bad_init_empty_file():
    with pytest.raises(ValueError):
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
    subtrees = build_pipeline("annotate -f tests/argfiles/annotation.csv -k taxon | subtree --attribute f1 --values 0", trees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        assert len(t.get_leaves()) == n
