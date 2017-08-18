"""Usage:
    phyltr height [<files>]

Print the heights of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Height(PhyltrCommand):

    def process_tree(self, t):
        print(t.get_farthest_leaf()[1])
        return None

def run():

    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    height = Height()
    plumb(height, files)
