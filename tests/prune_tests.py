import pytest

from phyltr.commands.prune import Prune
from phyltr.commands.annotate import Annotate

def test_init_from_args(argfilepath):
    prune = Prune.init_from_args("A,B,C")
    assert prune.opts.filename == None
    assert prune.opts.attribute == None
    assert prune.opts.values == None
    assert prune.opts.inverse == False

    prune = Prune.init_from_args("A,B,C --inverse")
    assert prune.opts.inverse == True

    taxa_abc = argfilepath('taxa_abc.txt')
    prune = Prune.init_from_args("--file {0}".format(taxa_abc))
    assert prune.opts.filename == taxa_abc
    assert prune.opts.attribute == None
    assert prune.opts.values == None

    prune = Prune.init_from_args("--attribute foo --values bar")
    assert prune.opts.filename == None
    assert prune.opts.attribute == "foo"
    assert prune.opts.values == ["bar"]

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Prune()

def test_bad_init_no_attribute_only():
    with pytest.raises(ValueError):
        Prune(attribute="foo")

def test_bad_init_no_value_only():
    with pytest.raises(ValueError):
        Prune(value="bar")

def test_bad_init_empty_file(emptyargs):
    with pytest.raises(ValueError):
        Prune(filename=emptyargs)

def test_prune(basictrees):
    pruned = Prune(taxa=["A"]).consume(basictrees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert "A" not in leaves
        assert all((x in leaves for x in ("B", "C", "D", "E", "F")))

def test_inverse_prune(basictrees):
    pruned = Prune(taxa=["A", "B"], inverse=True).consume(basictrees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("A", "B")))
        assert not any((x in leaves for x in ("C", "D", "E", "F")))

def test_file_prune(basictrees):
    pruned = Prune(filename="tests/argfiles/taxa_abc.txt").consume(basictrees)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert not any((x in leaves for x in ("A", "B", "C")))

def test_annotation_prune(basictrees, argfilepath):
    annotated = Annotate(filename=argfilepath("annotation.csv"), key="taxon").consume(basictrees)
    pruned = Prune(attribute="f1", values="0").consume(annotated)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert not any((x in leaves for x in ("A", "B", "C")))

def test_inverse_annotation_prune(basictrees):
    annotated = Annotate(filename="tests/argfiles/annotation.csv", key="taxon").consume(basictrees)
    pruned = Prune(attribute="f1", values="0", inverse=True).consume(annotated)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("A", "B", "C")))
        assert not any ((x in leaves for x in ("D", "E", "F")))
