"""Usage:
    phyltr scale [<options>] [<files>]

Scale the branch lengths in a treestream by a constant factor.

OPTIONS:

    -s, --scale
        The factor to scale by, expressed in floating point notation.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_stdin

class Scale(PhyltrCommand):

    def __init__(self, scalefactor=1.0):
        self.scalefactor = scalefactor

    def process_tree(self, t):
        for node in t.traverse():
            node.dist *= self.scalefactor
        return t


def init_from_args(*args):
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-s', '--scale', type="float", default=1.0,
                help='Scaling factor.')
    options, files = parser.parse_args(*args)

    scale = Scale(options.scale)
    return scale, files

def run():
    scale, files = init_from_args()
    plumb_stdin(scale, files)
