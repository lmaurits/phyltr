import pytest

from phyltr.commands.rename import Rename


def test_init(argfilepath):
    rename = Rename.init_from_args("--file {0} --from old --to new".format(argfilepath("rename.txt")))
    assert rename.opts.remove == False

    rename = Rename.init_from_args("--file {0} --from old --to new --remove-missing".format(argfilepath("rename.txt")))
    assert rename.opts.remove == True

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Rename()

def test_rename(basictrees):
    renamed = Rename(rename={"A":"X"}).consume(basictrees)
    for t in renamed:
        leaves = t.get_leaf_names()
        assert "A" not in leaves
        assert "X" in leaves
        assert all((x in leaves for x in ("B", "C", "D", "E", "F")))

def test_rename_from_file(basictrees):
    renamed = Rename(filename="tests/argfiles/rename.txt", from_="old", to_="new").consume(basictrees)
    for t in renamed:
        leaves = t.get_leaf_names()
        assert "A" not in leaves
        assert "X" in leaves
        assert all((x in leaves for x in ("B", "C", "D", "E", "F")))

def test_rename_with_remove(basictrees):
    renamed = Rename(rename={
        "A":"X",
        "B":"Y",
        "C":"Z" }, remove=True).consume(basictrees)
    for t in renamed:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("X", "Y", "Z")))
        assert not any((x in leaves for x in ("A", "B", "C", "D", "E", "F")))
