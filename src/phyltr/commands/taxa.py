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

    def process_tree(self, t):
        if self.done:
            raise StopIteration
        else:
            self.done = True
            return sorted([n.name for n in t.traverse() if n.name])
