import fileinput

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser
from phyltr.commands.cat import Cat

def test_init():
    # Test defaults
    cat = Cat.init_from_args("")
    assert cat.burnin == 0
    assert cat.subsample == 1
    assert cat.annotations == True

    # Test burnin
    cat = Cat.init_from_args("--burnin 10")
    assert cat.burnin == 10

    # Test subsample
    cat = Cat.init_from_args("--subsample 10")
    assert cat.subsample == 10

    # Test no annotations
    cat = Cat.init_from_args("--no-annotations")
    assert cat.annotations == False

def test_basic_cat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    trees = Cat().consume(trees)
    assert sum((1 for t in trees)) == 6

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

def test_beast_vector_annotated_nexus_output_cat():
    lines = fileinput.input("tests/treefiles/beast_output_geo_annotations.nex")
    trees = ComplexNewickParser().consume(lines)
    trees = Cat().consume(trees)
    for t in trees:
        for n in t.traverse():
            assert hasattr(n, "location")

def test_mr_bayes_nexus_output_cat():
    lines = fileinput.input("tests/treefiles/mr_bayes_output.nex")
    trees = ComplexNewickParser().consume(lines)
    trees = Cat().consume(trees)
    for t in trees:
        assert len(t.get_leaves()) == 12

