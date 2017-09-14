from __future__ import division

import fileinput

from phyltr.plumbing.sources import ComplexNewickParser, NewickParser
from phyltr.commands.consensus import Consensus

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
