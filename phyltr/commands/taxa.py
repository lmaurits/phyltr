"""Usage:
    phyltr taxa [<files>]

Extract the taxa names from the first tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import ListPerLineFormatter
from phyltr.utils.phyltroptparse import OptionParser

class Taxa(PhyltrCommand):

    sink = ListPerLineFormatter

    parser = OptionParser(__doc__, prog="phyltr taxa")

    def __init__(self):
        self.done = False

    @classmethod 
    def init_from_opts(cls, options, files):
        taxa = Taxa()
        return taxa

    def process_tree(self, t):
        if self.done:
            raise StopIteration
        else:
            names = [n.name for n in t.traverse() if n.name]
            self.done = True
            return sorted(names)
