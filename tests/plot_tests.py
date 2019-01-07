import fileinput
import tempfile
import os

import ete3

from phyltr.main import build_pipeline
from phyltr.plumbing.sources import NewickParser
from phyltr.commands.plot import Plot, ultrametric

def dummy_wrapper_for_travis(f):
    try:
        from ete3 import TreeStyle
        dummy = False
    except ImportError:
        dummy = True

    def test_wrapped():
        return f(dummy)
    return test_wrapped

@dummy_wrapper_for_travis
def test_init_from_args(dummy=False):
    if dummy:
        assert True
    else:
        plot = Plot.init_from_args("")

@dummy_wrapper_for_travis
def test_plot(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(dummy=dummy, output=fp.name, height=600, width=800)
        for x in plot.consume(trees):
            pass
    lines.close()

@dummy_wrapper_for_travis
def test_plot_multiple(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(dummy=dummy, output=fp.name, height=600, width=800, multiple=True)
        for x in plot.consume(trees):
            pass
    lines.close()

@dummy_wrapper_for_travis
def test_plot_annotated(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated_trees = build_pipeline("annotate --f tests/argfiles/annotation.csv -k taxon", source=trees)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(output=fp.name, attribute="f1", dummy=dummy)
        for x in plot.consume(annotated_trees):
            pass
    lines.close()


