import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.scale import Scale

def test_scale():
    scale_factor = 0.42
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    old_heights = [t.get_farthest_leaf()[1] for t in trees]
    scaled = Scale(scale_factor).consume(trees)
    new_heights = [t.get_farthest_leaf()[1] for t in scaled]
    for old, new in zip(old_heights, new_heights):
        assert new == old * scale_factor

