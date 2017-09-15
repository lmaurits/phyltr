import fileinput
import shlex

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser
from phyltr.commands.cat import Cat, init_from_args

def test_init_from_args():
    # Test defaults
    cat, files = init_from_args([])
    assert cat.burnin == 0
    assert cat.subsample == 1
    assert cat.annotations == True

    # Test burnin
    cat, files = init_from_args(shlex.split("--burnin 10"))
    assert cat.burnin == 10

    # Test subsample
    cat, files = init_from_args(shlex.split("--subsample 10"))
    assert cat.subsample == 10

    # Test no annotations
    cat, files = init_from_args(shlex.split("--no-annotations"))
    assert cat.annotations == False

def test_basic_cat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subsampled = Cat(subsample=2).consume(trees)
    assert sum((1 for t in subsampled)) == 3

def test_burnin():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    burntin = Cat(burnin=50).consume(trees)
    assert sum((1 for t in burntin)) == 3

def test_beast_nexus_output_cat():
    lines = fileinput.input("tests/treefiles/beast_output.nex")
    trees = ComplexNewickParser().consume(lines)
    trees = Cat().consume(trees)
    for t in trees:
        assert len(t.get_leaves()) == 26

def test_beast_annotated_nexus_output_cat():
    lines = fileinput.input("tests/treefiles/beast_output_rate_annotations.nex")
    trees = ComplexNewickParser().consume(lines)
    trees = Cat().consume(trees)
    for t in trees:
        for n in t.traverse():
            assert hasattr(n, "rate")
        assert len(t.get_leaves()) == 26
