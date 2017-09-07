import fileinput
import tempfile
import os

from phyltr.commands.generic import NewickParser
from phyltr.commands.plot import Plot

def test_plot():
    if os.environ.get("TRAVIS"):
        assert True

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    with tempfile.NamedTemporaryFile() as fp:
        plot = Plot(output=fp.name)
        for x in plot.consume(trees):
            pass
    lines.close()
