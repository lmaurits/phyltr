import fileinput

import pytest
from ete3 import Tree
from six import StringIO

from phyltr.plumbing.sources import ComplexNewickParser, get_tree
from phyltr.plumbing.sinks import NewickFormatter


@pytest.mark.parametrize(
    'kw,in_,out',
    [
        (dict(topology_only=True), '(A:1,(B:1,(E:1,D:1):0.5):0.5);', '(A,(B,(E,D)));'),
        (dict(annotations=False), '(A:1,(B:1,(E:1,D:1):0.5));', '(A:1,(B:1,(E:1,D:1)1:0.5)1:1);'),
    ]
)
def test_NewickFormatter(kw, in_, out):
    buf = StringIO()
    nf = NewickFormatter(out=buf, **kw)
    nf.consume([Tree(in_)])
    buf.seek(0)
    assert buf.read().strip() == out


def test_ComplexNewickParser():
    p = ComplexNewickParser()
    fileinput._state = None
    assert list(p.consume(['A', 'B'])) == []

    # A burnin of 1% won't actually skip any trees, but will force writing to and yielding from
    # a temp file.
    p = ComplexNewickParser(burnin=1)
    fileinput._state = None
    # The second tree should be discarded due to malformedness:
    t = list(p.consume(['(A);', '(A,(,B,));']))[0]
    assert [l.name for l in t.get_leaves()] == ['A']


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
    root = get_tree(newick)[0].get_tree_root()
    for attr, value in attrs.items():
        if isinstance(value, float):
            assert getattr(root, attr) == pytest.approx(value)
        else:
            assert getattr(root, attr) == value


def test_get_tree_wrong_format():
    # Try to read  a tree with format 0 ...
    res = get_tree("(A:1,(B:1,(E:1,D:1)Internal_1:0.5)Internal_2:0.5)Root;", newick_format=0)
    # ... but get told it can only be read with format 1:
    assert res[2] == 1
