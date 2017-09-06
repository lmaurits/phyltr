import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.stat import Stat

def test_stat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    stat = Stat()
    stat.consume(trees)
    assert stat.tree_count == 6
    assert stat.taxa_count == 6
    assert stat.topology_count <= stat.tree_count
