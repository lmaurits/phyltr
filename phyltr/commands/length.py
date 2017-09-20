"""Usage:
    phyltr length [<files>]

Print the length of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import optparse

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter

class Length(PhyltrCommand):

    sink = StringFormatter

    parser = optparse.OptionParser(add_help_option = False)
    parser.add_option('-h', '--help', action="store_true", dest="help", default=False)

    @classmethod 
    def init_from_opts(cls, options, files):
        length = Length()
        return length

    def process_tree(self, t):
        return sum([n.dist for n in t.traverse()])
