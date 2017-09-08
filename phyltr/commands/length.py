"""Usage:
    phyltr length [<files>]

Print the length of each tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.generic import PhyltrCommand, plumb_strings
import phyltr.utils.phyoptparse as optparse

class Length(PhyltrCommand):

    def process_tree(self, t):
        return sum([n.dist for n in t.traverse()])

def run():

    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    length = Length()
    plumb_strings(length, files)
