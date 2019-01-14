import pytest

from phyltr.main import build_pipeline
from phyltr.commands.plot import Plot


@pytest.fixture
def with_ete3():
    try:
        from ete3 import TreeStyle
        return True
    except ImportError:
        return False

def test_init_from_args(with_ete3):
    if not with_ete3:
        assert True
    else:
        Plot.init_from_args("")

def test_plot(tmpdir, basictrees, with_ete3):
    plot = Plot(dummy=not with_ete3, output=str(tmpdir.join('test')), height=600, width=800)
    list(plot.consume(basictrees))

def test_plot_multiple(tmpdir, basictrees, with_ete3):
    plot = Plot(dummy=not with_ete3, output=str(tmpdir.join('test')), height=600, width=800, multiple=True)
    list(plot.consume(basictrees))

def test_plot_annotated(tmpdir, basictrees, with_ete3):
    annotated_trees = build_pipeline("annotate --f tests/argfiles/annotation.csv -k taxon", source=basictrees)
    plot = Plot(output=str(tmpdir.join('test')), attribute="f1", dummy=not with_ete3)
    list(plot.consume(annotated_trees))
