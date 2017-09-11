import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.height import Height

def test_height():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    heights = Height().consume(trees)
    for h in heights:
        assert type(h) == float
        assert h >= 0.0
