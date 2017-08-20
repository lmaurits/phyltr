import fileinput

from phyltr.commands.generic import NewickParser

def test_parsing():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    assert sum((1 for t in trees)) == 6
