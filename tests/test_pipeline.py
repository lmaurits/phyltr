from phyltr import build_pipeline

def test_pipeline(basictrees, argfilepath):
    """Silly long pipeline to stress test build_pipeline."""
    output = build_pipeline(
        "cat -s 2 | rename -f {0} --from old --to new | prune X B | dedupe | uniq | support --sort | stat".format(
            argfilepath('rename.txt')),
        source=basictrees)
    for t in output:
        leaves = t.get_leaf_names()
        assert all((leaves.count(x) == 1  for x in leaves))
        assert "A" not in leaves
        assert "X" not in leaves
        assert "B" not in leaves
        assert all((x in leaves for x in ("C", "D", "E", "F")))

def test_implicit_source(treefilepath, argfilepath):
    output = build_pipeline(
        "cat -s 2 | rename -f {0} --from old --to new | prune X B | dedupe | uniq | support --sort | stat".format(
            argfilepath('rename.txt')),
        source=treefilepath("basic.trees"))
    for t in output:
        leaves = t.get_leaf_names()
        assert all((leaves.count(x) == 1  for x in leaves))
        assert "A" not in leaves
        assert "X" not in leaves
        assert "B" not in leaves
        assert all((x in leaves for x in ("C", "D", "E", "F")))
