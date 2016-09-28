"""Usage:
    phyltr annotate [<options>] [<files>]

Annotate a the trees in a tree stream with information from a file

OPTIONS:

    -f, --file
        File to read annotations from

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import csv
import fileinput
import sys

import ete2

import phyltr.utils.phyoptparse as optparse

def read_annotation_file(filename, key):
    annotations = {}
    fp = open(filename, "r")
    dialect = csv.Sniffer().sniff(fp.read(1024))
    fp.seek(0)
    dr = csv.DictReader(fp, dialect=dialect)
    assert key in dr.fieldnames
    for row in dr:
        this_key = row.pop(key)
        annotations[this_key] = row
    fp.close()
    return annotations

def annotate_tree(t, annotations):
    for node in t.traverse():
        if node.name in annotations:
            for key, value in annotations[node.name].items():
                node.add_feature(key, value)

def extract_annotations(t, filename, tree_no=None):
    if filename == "-" or not filename:
        fp = sys.stdout
    else:
        if tree_no and tree_no > 1:
            fp = open(filename, "a")
        else:
            fp = open(filename, "w")
    features = []
    for node in t.traverse():
        for f in node.features:
            if f not in ["dist", "support", "name"] and f not in features:
                features.append(f)
    features.sort()
    fieldnames = ["name"]
    if tree_no:
        fieldnames.append("tree_number")
    fieldnames.extend(features)
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    if tree_no in (None, 1):
        writer.writeheader()
    for node in t.traverse():
        # Only include the root node or nodes with names
        if not node.name and node.up:
            continue
        if any([hasattr(node,f) for f in features]):
            if not node.name:
                # Temporarily give the node a name
                node.name = "root"
                fix_root_name = True
            else:
                fix_root_name = False
            rowdict = {f:getattr(node, f, "?") for f in fieldnames}
            if tree_no:
                rowdict["tree_number"] = tree_no
            writer.writerow(rowdict)
            if fix_root_name:
                node.name = None
    if filename == "-" or not filename:
        pass
    else:
        fp.close()

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-e', '--extract', action="store_true", help="Extract data from annotated tree to file.")
    parser.add_option('-f', '--file', dest="filename", help="File to read/write annotation data from/to.")
    parser.add_option('-k', '--key', dest="key", help="Name of column in annotation file to match against taxon names")
    parser.add_option('-m', '--multiple', default=False, action="store_true")
    options, files = parser.parse_args()

    # Read annotation file
    if not options.extract:
        annotations = read_annotation_file(options.filename, options.key)

    # Read trees and annotate them
    for n, line in enumerate(fileinput.input(files)):
        t = ete2.Tree(line)
        if options.extract:
            if options.multiple:
                extract_annotations(t, options.filename, n+1)
            else:
                extract_annotations(t, options.filename)
        else:
            annotate_tree(t, annotations)

        if options.extract:
            if not options.multiple:
                return 0
            if options.filename == "-":
                # Suppress output
                continue
        print t.write(features=[],format_root_node=True)

    # Done
    return 0
