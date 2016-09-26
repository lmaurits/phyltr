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

def extract_annotations(t, filename):
    fp = open(filename, "w")
    features = []
    for node in t.traverse():
        for f in node.features:
            if f not in ["dist", "support", "name"] and f not in features:
                features.append(f)
    features.sort()
    fieldnames = ["name"]
    fieldnames.extend(features)
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for node in t.traverse():
        if any([hasattr(node,f) for f in features]):
            writer.writerow({f:getattr(node, f, "?") for f in fieldnames})
    fp.close()

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-e', '--extract', action="store_true", help="Extract data from annotated tree to file.")
    parser.add_option('-f', '--file', dest="filename", help="File to read/write annotation data from/to.")
    parser.add_option('-k', '--key', dest="key", help="Name of column in annotation file to match against taxon names")
    options, files = parser.parse_args()

    # Read annotation file
    if not options.extract:
        annotations = read_annotation_file(options.filename, options.key)

    # Read trees and annotate them
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        if options.extract:
            pass
            extract_annotations(t, options.filename)
        else:
            annotate_tree(t, annotations)
        print t.write(features=[])

    # Done
    return 0
