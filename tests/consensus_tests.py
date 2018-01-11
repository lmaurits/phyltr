import fileinput

from phyltr.plumbing.sources import ComplexNewickParser, NewickParser
from phyltr.commands.consensus import Consensus
from phyltr.commands.length import Length

def test_init_from_args():
    consensus = Consensus.init_from_args("")
    assert consensus.frequency == 0.5

    consensus = Consensus.init_from_args("-f 0.42")
    assert consensus.frequency == 0.42

def test_consensus():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    consensus = list(Consensus().consume(trees))
    assert len(consensus) == 1

def test_low_freq_consensus():
    lines = fileinput.input("tests/treefiles/beast_output.nex")
    trees = ComplexNewickParser().consume(lines)
    consensus = list(Consensus(frequency=0.25).consume(trees))
    assert len(consensus) == 1

def test_annotation_consensus():
    lines = fileinput.input("tests/treefiles/beast_output_rate_annotations.nex")
    trees = ComplexNewickParser().consume(lines)
    consensus = list(Consensus().consume(trees))[0]
    for n in consensus.traverse():
        for attr in ("rate_mean", "rate_median", "rate_HPD"):
            assert hasattr(n, attr)

def test_min_med_max_consensus():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))

    min_uniq = Consensus(lengths="min").consume(trees)
    min_lengths = Length().consume(min_uniq)

    med_uniq = Consensus(lengths="median").consume(trees)
    med_lengths = Length().consume(med_uniq)

    max_uniq = Consensus(lengths="max").consume(trees)
    max_lengths = Length().consume(max_uniq)

    for l, m, L in zip(min_lengths, med_lengths, max_lengths):
        assert l <= m <= L
