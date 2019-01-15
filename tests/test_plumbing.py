import fileinput

import pytest

from phyltr.plumbing.sources import ComplexNewickParser, get_tree, BEAST_ANNOTATION_REGEX_2


def test_ComplexNewickParser():
    p = ComplexNewickParser()
    fileinput._state = None
    assert list(p.consume(['A', 'B'])) == []


@pytest.mark.parametrize(
    'newick,attrs',
    [
        (
            '(A,B)C;',
            dict(name='C', dist=0.0)),
        (
            '(A:0.5,B:0.5)C:0.5;',
            dict(name='C', dist=0.5)),
        (
            '(A:0.5,B:0.5)[&rate=0.123E-4,location={12.3,4.56}]:0.5e1;',
            dict(name='', dist=0.5e1, rate='0.123E-4', location='{12.3|4.56}')),
        (
            '(A:0.5,B:0.5):[&rate=0.123E-4,location={12.3,4.56}]0.5E;',
            dict(name='', dist=0.5, rate='0.123E-4', location='{12.3|4.56}')),
        (
            '(A:0.5,B:0.5)C:0.5@0.7;',
            dict(name='C', rate='0.7', dist=0.5)),
    ]
)
def test_get_tree(newick, attrs):
    root = get_tree(newick).get_tree_root()
    for attr, value in attrs.items():
        if isinstance(value, float):
            assert getattr(root, attr) == pytest.approx(value)
        else:
            assert getattr(root, attr) == value
