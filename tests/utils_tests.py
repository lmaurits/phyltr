from collections import namedtuple
import argparse

import pytest

from phyltr.utils import misc
from phyltr.utils import cladeprob
from phyltr.utils import phyltroptparse


@pytest.mark.parametrize(
    'spec,expected',
    [
        (dict(attribute='attr', values='0,1'), ['a', 'b']),
        (dict(attribute='attr', values='0,1', inverse=True), list('cdefghij')),
        (dict(attribute='x', values='0,1'), []),  # invalid attribute - no leafs match!
        (dict(attribute='x', values='0,1', inverse=True), list('abcdefghij')),
        (dict(taxa=list('cde')), list('cde')),
        (dict(taxa=list('cde'), inverse=True), list('abfghij')),
    ]
)
def test_selector_from_taxa_spec(spec, expected):
    Leaf = namedtuple('Leaf', ['name', 'attr'])
    leafset = [Leaf(n, str(a)) for n, a in zip('abcdefghij', range(10))]
    opts = dict(taxa=[], attribute=None, values=None, filename=None)
    opts.update(spec)
    selector = phyltroptparse.selector_from_taxa_spec(argparse.Namespace(**opts))
    assert [l.name for l in leafset if selector(l)] == expected


def test_parse_float():
    assert cladeprob.parse_float("""'"1.0"'""") == pytest.approx(1.0)

    with pytest.raises(ValueError):
        cladeprob.parse_float("'x1.0'")


def test_default():
    assert misc.DEFAULT not in [None, 0, []]

    class A:
        b = None

    assert getattr(A(), 'b', misc.DEFAULT) == None
    assert getattr(A(), 'c', misc.DEFAULT) != None
