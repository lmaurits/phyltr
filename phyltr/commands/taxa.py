"""Usage:
    phyltr taxa [<files>]

Extract the taxa names from the first tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import optparse

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import ListPerLineFormatter

class Taxa(PhyltrCommand):

    sink = ListPerLineFormatter

    parser = optparse.OptionParser(add_help_option = False)
    parser.add_option('-h', '--help', action="store_true", dest="help", default=False)

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
