from phyltr.commands.stat import Stat

def test_stat(basictrees):
    stat = Stat()
    list(stat.consume(basictrees))
    assert stat.tree_count == 6
    assert stat.taxa_count == 6
    assert stat.topology_count <= stat.tree_count
