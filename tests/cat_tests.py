import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.cat import Cat

def test_cat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    subsampled = Cat(subsample=2).consume(trees)
    assert sum((1 for t in subsampled)) == 3
