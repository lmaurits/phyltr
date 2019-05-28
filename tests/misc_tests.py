from phyltr.utils import misc


def test_default():
    assert misc.DEFAULT not in [None, 0, []]

    class A:
        b = None

    assert getattr(A(), 'b', misc.DEFAULT) == None
    assert getattr(A(), 'c', misc.DEFAULT) != None
