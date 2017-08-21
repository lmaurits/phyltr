import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.uniq import Uniq

def test_uniq():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    uniq = Uniq().consume(trees)
    # The 6 basic trees comprise 5 unique topologies.
    # This is a pretty weak test, but...
    assert sum((1 for t in uniq)) == 5
