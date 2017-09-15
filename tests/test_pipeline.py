import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline

def test_pipeline():
    """Silly long pipeline to stress test build_pipeline."""

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    output = build_pipeline("cat -s 2 | rename -f tests/argfiles/rename.txt | prune X,B | dedupe | uniq | support --sort | stat", source=trees)
    for t in output:
        print(t.write())
        leaves = t.get_leaf_names()
        assert all((leaves.count(x) == 1  for x in leaves))
        assert "A" not in leaves
        assert "X" not in leaves
        assert "B" not in leaves
        assert all((x in leaves for x in ("C", "D", "E", "F")))
