import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline
from phyltr.commands.height import Height
from phyltr.commands.length import Length
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

def test_identity():
    """Make sure scaling with a factor of 1.0 changes nothing."""

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    unscaled_trees = Scale(1.0).consume(trees)
    for t1, t2 in zip(trees, unscaled_trees):
        assert t1.write() == t2.write()

def test_roundtrip():
    """Make sure scaling by x and then 1/x changes nothing."""
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))

    heights = Height().consume(trees)
    scaled_heights = build_pipeline("scale -s 2.0 | scale -s 0.5 | height", trees)
    for x, y in zip(heights, scaled_heights):
        assert x == y

    lengths = Length().consume(trees)
    scaled_lengths = build_pipeline("scale -s 2.0 | scale -s 0.5 | length", trees)
    for x, y in zip(lengths, scaled_lengths):
        assert x == y
