import fileinput

from phyltr.plumbing.sources import ComplexNewickParser


def test_ComplexNewickParser():
    p = ComplexNewickParser()
    fileinput._state = None
    assert list(p.consume(['A', 'B'])) == []
