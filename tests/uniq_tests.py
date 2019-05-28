from phyltr.commands.uniq import Uniq
from phyltr.commands.length import Length

def test_init_from_args():
    uniq = Uniq.init_from_args("")
    assert uniq.opts.lengths == "mean"

    for lengths in ("min", "max", "median"):
        uniq = Uniq.init_from_args("--lengths %s" % lengths)
        assert uniq.opts.lengths == lengths

def test_uniq(basictrees, tmpdir):
    uniq = Uniq(separate=True, output=str(tmpdir)).consume(basictrees)
    # The 6 basic trees comprise 5 unique topologies.
    # This is a pretty weak test, but...
    assert sum((1 for t in uniq)) == 5
    assert tmpdir.join('phyltr_uniq_5.trees').check()

def test_min_med_max_uniq(basictrees):
    min_uniq = Uniq(lengths="min").consume(basictrees)
    min_lengths = Length().consume(min_uniq)

    med_uniq = Uniq(lengths="median").consume(basictrees)
    med_lengths = Length().consume(med_uniq)

    max_uniq = Uniq(lengths="max").consume(basictrees)
    max_lengths = Length().consume(max_uniq)

    for l, m, L in zip(min_lengths, med_lengths, max_lengths):
        assert l <= m <= L
