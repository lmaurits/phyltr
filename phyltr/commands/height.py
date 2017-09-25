"""Usage:
    phyltr height [<files>]

Print the heights of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter
from phyltr.utils.phyltroptparse import OptionParser

class Height(PhyltrCommand):

    sink = StringFormatter

    parser = OptionParser(__doc__, prog="phyltr height")

    @classmethod 
    def init_from_opts(cls, options, files):
        height = Height()
        return height

    def process_tree(self, t):
        return t.get_farthest_leaf()[1]
