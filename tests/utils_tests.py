import pytest

from phyltr.utils import misc
from phyltr.utils import cladeprob


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
