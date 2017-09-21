import fileinput
import tempfile
import os

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline
from phyltr.commands.plot import Plot

def travis_dummy_test_wrapper(f):
    if os.environ.get("TRAVIS"):
        dummy = True
    else:
        dummy = False
    def wrapped():
        return f(dummy)
    return wrapped

@travis_dummy_test_wrapper
def test_init_from_args(dummy=False):
    if dummy:
        assert True
    else:
        plot = Plot.init_from_args("")

@travis_dummy_test_wrapper
def test_plot(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(dummy=dummy, output=fp.name, height=600, width=800)
        for x in plot.consume(trees):
            pass
    lines.close()

@travis_dummy_test_wrapper
def test_plot_multiple(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(dummy=dummy, output=fp.name, height=600, width=800, multiple=True)
        for x in plot.consume(trees):
            pass
    lines.close()

@travis_dummy_test_wrapper
def test_plot_annotated(dummy=False):

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated_trees = build_pipeline("annotate --f tests/argfiles/annotation.csv -k taxon", source=trees)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(output=fp.name, attribute="f1", dummy=dummy)
        for x in plot.consume(annotated_trees):
            pass
    lines.close()


