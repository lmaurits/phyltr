"""Usage:
    phyltr annotate [<options>] [<files>]

Annotate a the trees in a tree stream with information from a file

OPTIONS:

    -e, --extract
        Build a CSV file of information from a treestream, i.e. reverse the
        standard behaviour

    -f, --file
        File to read annotations from

    -k, --key
        Fieldname which corresponds to tree taxon names, used to link lines
        of the csv file to tree nodes.

    -m, --multiple
        If set, when --extract is used, information from each tree in the
        treestream will be added to the file, with a `tree_number` column
        used to disambiguate.  When not set, information is extracted only
        from the first tree in the treestream.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import csv
import optparse
import sys

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import NullSink

class Annotate(PhyltrCommand):

    parser = optparse.OptionParser(add_help_option = False)
    parser.add_option('-h', '--help', action="store_true", dest="help", default=False)
    parser.add_option('-e', '--extract', default=False, action="store_true", help="Extract data from annotated tree to file.")
    parser.add_option('-f', '--file', dest="filename", help="File to read/write annotation data from/to.")
    parser.add_option('-k', '--key', dest="key", help="Name of column in annotation file to match against taxon names")
    parser.add_option('-m', '--multiple', default=False, action="store_true")

    def __init__(self, filename, key=None, extract=False, multiple=False):
        self.filename = filename
        self.key = key
        self.extract = extract
        self.multiple = multiple

        self.n = 0

        if not self.extract:
            self.read_annotation_file()

    @classmethod 
    def init_from_opts(cls, options, files=[]):
        annotate = Annotate(options.filename, options.key, options.extract, options.multiple)
        if annotate.extract and (annotate.filename == "-" or not annotate.filename):
            # If we're writing an extracted CSV to stdin, we don't want to also
            # serialise the trees, so plumb to null
            cls.sink = NullSink

        return annotate

    def process_tree(self, t):
        if self.extract:
            # Break out of consume if we've done one
            if not self.multiple:
                if self.n > 0:
                    raise StopIteration
            self.extract_annotations(t)
        else:
            self.annotate_tree(t)
        self.n += 1
        return t

    def read_annotation_file(self):
        self.annotations = {}
        fp = open(self.filename, "r")
        dialect = csv.Sniffer().sniff(fp.read(1024))
        fp.seek(0)
        dr = csv.DictReader(fp, dialect=dialect)
        assert self.key in dr.fieldnames
        for row in dr:
            this_key = row.pop(self.key)
            self.annotations[this_key] = row
        fp.close()

    def annotate_tree(self, t):
        for node in t.traverse():
            if node.name in self.annotations:
                for key, value in self.annotations[node.name].items():
                    node.add_feature(key, value)

    def extract_annotations(self, t):
        if self.filename == "-" or not self.filename:
            fp = sys.stdout # pragma: no cover
        else:
            if self.n > 0:
                fp = open(self.filename, "a")
            else:
                fp = open(self.filename, "w")
        features = []
        for node in t.traverse():
            for f in node.features:
                if f not in ["dist", "support", "name"] and f not in features:
                    features.append(f)
        features.sort()
        fieldnames = ["name"]
        if self.multiple:
            fieldnames.append("tree_number")
        fieldnames.extend(features)
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        if self.n == 0:
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
                if self.multiple:
                    rowdict["tree_number"] = self.n
                writer.writerow(rowdict)
                if fix_root_name:
                    node.name = None
        if self.filename and self.filename != "-":
            fp.close()
