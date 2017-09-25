import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.length import Length

def test_length():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    lengths = Length().consume(trees)
    for l in lengths:
        assert type(l) == float
        assert l >= 0.0
