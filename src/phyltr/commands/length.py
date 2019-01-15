"""Usage:
    phyltr length [<files>]

Print the length of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter
from phyltr.utils.phyltroptparse import OptionParser

class Length(PhyltrCommand):

    sink = StringFormatter

    parser = OptionParser(__doc__, prog="phyltr length")

    def process_tree(self, t):
        return sum([n.dist for n in t.traverse()])
