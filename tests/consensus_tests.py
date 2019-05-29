from phyltr.commands.consensus import Consensus
from phyltr.commands.length import Length

def test_init_from_args():
    consensus = Consensus.init_from_args("")
    assert consensus.opts.frequency == 0.5

    consensus = Consensus.init_from_args("-f 0.42")
    assert consensus.opts.frequency == 0.42

def test_consensus(basictrees):
    consensus = list(Consensus().consume(basictrees))
    assert len(consensus) == 1

def test_low_freq_consensus(treefilenewick):
    consensus = list(Consensus(frequency=0.25).consume(treefilenewick('beast_output.nex')))
    assert len(consensus) == 1

def test_annotation_consensus(treefilenewick):
    consensus = list(Consensus().consume(treefilenewick('beast_output_rate_annotations.nex')))[0]
    for n in consensus.traverse():
        for attr in ("rate_mean", "rate_median", "rate_HPD"):
            assert hasattr(n, attr)

def test_min_med_max_consensus(basictrees):
    trees = list(basictrees)

    min_uniq = Consensus(lengths="min").consume(trees)
    min_lengths = Length().consume(min_uniq)

    med_uniq = Consensus(lengths="median").consume(trees)
    med_lengths = Length().consume(med_uniq)

    max_uniq = Consensus(lengths="max").consume(trees)
    max_lengths = Length().consume(max_uniq)

    res = list(zip(min_lengths, med_lengths, max_lengths))
    print(res)

    for l, m, L in res:
        assert l <= m <= L
