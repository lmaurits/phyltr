import fileinput

from phyltr.commands.generic import NewickParser, ComplexNewickParser
from phyltr.commands.cat import Cat

def test_basic_cat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subsampled = Cat(subsample=2).consume(trees)
    assert sum((1 for t in subsampled)) == 3

def test_beast_nexus_output_cat():
    lines = fileinput.input("tests/treefiles/beast_output.nex")
    trees = ComplexNewickParser().consume(lines)
    trees = Cat().consume(trees)
    for t in trees:
        assert len(t.get_leaves()) == 26
