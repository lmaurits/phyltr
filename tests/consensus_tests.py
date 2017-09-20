import fileinput

from phyltr.plumbing.sources import ComplexNewickParser, NewickParser
from phyltr.commands.consensus import Consensus

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

def test_annotation_consensus():
    lines = fileinput.input("tests/treefiles/beast_output_rate_annotations.nex")
    trees = ComplexNewickParser().consume(lines)
    consensus = list(Consensus().consume(trees))[0]
    for n in consensus.traverse():
        for attr in ("rate_mean", "rate_median", "rate_HPD"):
            assert hasattr(n, attr)
