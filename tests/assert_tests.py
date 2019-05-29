from phyltr import COMMANDS

Assert = COMMANDS['assert']


def test_assert(basictrees):
    trees = Assert().consume(basictrees)
    assert sum((1 for _ in trees)) == 6
