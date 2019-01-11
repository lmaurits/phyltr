from phyltr.commands.cat import Cat


def test_basic_cat(basictrees):
    trees = Cat().consume(basictrees)
    assert sum((1 for _ in trees)) == 6

def test_beast_nexus_output_cat(treefilenewick):
    trees = Cat().consume(treefilenewick('beast_output.nex'))
    for t in trees:
        assert len(t.get_leaves()) == 26

def test_beast_annotated_nexus_output_cat(treefilenewick):
    trees = Cat().consume(treefilenewick('beast_output_rate_annotations.nex'))
    for t in trees:
        for n in t.traverse():
            assert hasattr(n, "rate")
        assert len(t.get_leaves()) == 26

def test_beast_vector_annotated_nexus_output_cat(treefilenewick):
    trees = Cat().consume(treefilenewick('beast_output_geo_annotations.nex'))
    for t in trees:
        for n in t.traverse():
            assert hasattr(n, "location")

def test_mr_bayes_nexus_output_cat(treefilenewick):
    trees = Cat().consume(treefilenewick('mr_bayes_output.nex'))
    for t in trees:
        assert len(t.get_leaves()) == 12
