"""Usage:
    phyltr height [<files>]

Print the heights of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_strings

class Height(PhyltrCommand):

    def process_tree(self, t):
        return t.get_farthest_leaf()[1]


def init_from_args(*args):
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args(*args)
    
    height = Height()
    return height, files

def run():  # pragma: no cover
    height, files = init_from_args()
    plumb_strings(height, files)
