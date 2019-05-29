from phyltr import build_pipeline
from phyltr.commands.height import Height
from phyltr.commands.length import Length
from phyltr.commands.scale import Scale

def test_init_from_args():
    scale = Scale.init_from_args("")
    assert scale.opts.scalefactor == 1.0

    scale = Scale.init_from_args("--scale 4.2")
    assert scale.opts.scalefactor == 4.2

def test_scale(basictrees):
    scale_factor = 0.42
    old_heights = [t.get_farthest_leaf()[1] for t in basictrees]
    scaled = Scale(scalefactor=scale_factor).consume(basictrees)
    new_heights = [t.get_farthest_leaf()[1] for t in scaled]
    for old, new in zip(old_heights, new_heights):
        assert new == old * scale_factor

def test_identity(basictrees):
    """Make sure scaling with a factor of 1.0 changes nothing."""
    unscaled_trees = Scale(scalefactor=1.0).consume(basictrees)
    for t1, t2 in zip(basictrees, unscaled_trees):
        assert t1.write() == t2.write()

def test_roundtrip(basictrees):
    """Make sure scaling by x and then 1/x changes nothing."""
    heights = Height().consume(basictrees)
    scaled_heights = build_pipeline("scale -s 2.0 | scale -s 0.5 | height", basictrees)
    for x, y in zip(heights, scaled_heights):
        assert x == y

    lengths = Length().consume(basictrees)
    scaled_lengths = build_pipeline("scale -s 2.0 | scale -s 0.5 | length", basictrees)
    for x, y in zip(lengths, scaled_lengths):
        assert x == y
