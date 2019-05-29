import pytest

from phyltr import build_pipeline
from phyltr.commands.subtree import Subtree

def test_init_from_args():
    subtree = Subtree.init_from_args("--file tests/argfiles/taxa_abc.txt")
    assert subtree.opts.attribute == None
    assert subtree.opts.filename == "tests/argfiles/taxa_abc.txt"
    assert subtree.opts.values == None

    subtree = Subtree.init_from_args("--attribute foo --values bar,baz")
    assert subtree.opts.attribute == "foo"
    assert subtree.opts.filename == None
    assert subtree.opts.values == ["bar", "baz"]

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Subtree()

def test_bad_init_no_attribute_only():
    with pytest.raises(ValueError):
        Subtree(attribute="foo")

def test_bad_init_no_value_only():
    with pytest.raises(ValueError):
        Subtree(values="bar")

def test_bad_init_empty_file(emptyargs):
    with pytest.raises(ValueError):
        Subtree(filename=emptyargs)


def extracted_taxa(subtrees):
    return [[l.name for l in t.get_leaves()] for t in subtrees]


def test_subtree(basictrees):
    subtree = Subtree.init_from_args("A B C")
    subtrees = subtree.consume(basictrees)
    assert [3, 3, 3, 3, 3, 6] == [len(t) for t in extracted_taxa(subtrees)]

def test_subtree_2(basictrees):
    subtree = Subtree.init_from_args("A B F")
    subtrees = subtree.consume(basictrees)
    assert [6, 6, 6, 6, 6, 3] == [len(t) for t in extracted_taxa(subtrees)]

def test_file_subtree(basictrees):
    subtrees = Subtree(filename="tests/argfiles/taxa_abc.txt").consume(basictrees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        assert len(t.get_leaves()) == n

def test_annotation_subtree(basictrees):
    subtrees = build_pipeline(
        "annotate -f tests/argfiles/annotation.csv -k taxon | subtree --attribute f1 --values 0", basictrees)
    expected_taxa = (3, 3, 3, 3, 3, 6)
    for t, n in zip(subtrees, expected_taxa):
        assert len(t.get_leaves()) == n

    subtrees = build_pipeline(
        "annotate -f tests/argfiles/annotation.csv -k taxon | subtree --attribute f1 --values 1", basictrees)
    taxa = extracted_taxa(subtrees)
    subtrees = build_pipeline(
        "annotate -f tests/argfiles/annotation.csv -k taxon | subtree D E F", basictrees)
    assert taxa == extracted_taxa(subtrees)
