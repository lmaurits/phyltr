import fileinput
import shlex

from nose.tools import raises

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.prune import Prune, init_from_args
from phyltr.commands.annotate import Annotate
from phyltr.commands.height import Height

def test_init_from_args():
    prune, files = init_from_args(shlex.split("A,B,C"))
    assert prune.taxa == set(("A","B","C"))
    assert prune.filename == None
    assert prune.attribute == None
    assert prune.value == None
    assert prune.inverse == False

    prune, files = init_from_args(shlex.split("A,B,C --inverse"))
    assert prune.inverse == True

    prune, files = init_from_args(shlex.split("--file tests/argfiles/taxa_abc.txt"))
    print(prune.taxa)
    assert prune.taxa == set(("A","B","C"))
    assert prune.filename == "tests/argfiles/taxa_abc.txt"
    assert prune.attribute == None
    assert prune.value == None
    prune, files = init_from_args(shlex.split("--attribute foo --value bar"))
    assert prune.taxa == []
    assert prune.filename == None
    assert prune.attribute == "foo"
    assert prune.value == "bar"

@raises(ValueError)
def test_bad_init_no_args():
    Prune()

@raises(ValueError)
def test_bad_init_no_attribute_only():
    Prune(attribute="foo")

@raises(ValueError)
def test_bad_init_no_value_only():
    Prune(value="bar")

@raises(ValueError)
def test_bad_init_empty_file():
    Prune(filename="tests/argfiles/empty.txt")

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
        leaves = t.get_leaf_names()
        assert not any((x in leaves for x in ("A", "B", "C")))

def test_inverse_annotation_prune():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated = Annotate(filename="tests/argfiles/annotation.csv", key="taxon").consume(trees)
    pruned = Prune(attribute="f1", value="0", inverse=True).consume(annotated)
    for t in pruned:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("A", "B", "C")))
        assert not any ((x in leaves for x in ("D", "E", "F")))

