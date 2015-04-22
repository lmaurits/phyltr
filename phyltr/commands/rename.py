import fileinput
import optparse

import ete2

def read_rename_file(filename):

    """Read a file of names and their desired replacements and return a
    dictionary of this data."""

    rename = {}
    fp = open(filename, "r")
    for line in fp:
        old, new = line.strip().split(":")
        rename[old] = new
    fp.close()
    return rename

def run():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', destination="filename",
                help='Specifies the translation file.')
    options, files = parser.parse_args()

    # Read translation file
    try:
        rename = read_rename_file(options.translate)
    except IOError:
        return 1

    # Read trees
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        # Rename nodes
        for node in t.traverse():
            if node.name in rename:
                node.name = rename[node.name]

        # Output
        print t.write()

    # Done
    return 0
