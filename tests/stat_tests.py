import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.stat import Stat

def test_stat():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    stat = Stat()
    for t in stat.consume(trees):
        pass
    print(stat.tree_count)
    assert stat.tree_count == 6
    print(stat.taxa_count)
    assert stat.taxa_count == 6
    assert stat.topology_count <= stat.tree_count
