import csv
import sys

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import NullSink
from phyltr.utils.misc import dicts_from_csv


class Annotate(PhyltrCommand):
    """Annotate a the trees in a tree stream with information from a file"""
    __options__ = [
        (
            ('-e', '--extract'),
            dict(
                default=False,
                action="store_true",
                help="Build a CSV file of information from a treestream, i.e. reverse the"
                     "standard behaviour")),
        (
            ('-f', '--file'),
            dict(dest="filename", help="File to read/write annotation data from/to.")),
        (
            ('-k', '--key'),
            dict(help="Fieldname which corresponds to tree taxon names, used to link lines of the "
                      "csv file to tree nodes.")),
        (
            ('-m', '--multiple'),
            dict(
                default=False, action="store_true",
                help="If set, when --extract is used, information from each tree in the treestream "
                     "will be added to the file, with a `tree_number` column used to disambiguate. "
                     "When not set, information is extracted only from the first tree in the "
                     "treestream.")),
    ]

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.annotations = {}

        if self.opts.extract and (self.opts.filename == "-" or not self.opts.filename):
            # If we're writing an extracted CSV to stdin, we don't want to also
            # serialise the trees, so plumb to null
            self.sink = NullSink

        if not self.opts.extract:
            self.read_annotation_file()

    def process_tree(self, t, n):
        if self.opts.extract:
            # Break out of consume if we've done one
            if not self.opts.multiple and n > 1:
                raise StopIteration
            self.extract_annotations(t, n)
        else:
            self.annotate_tree(t)
        return t

    def read_annotation_file(self):
        for row in dicts_from_csv(self.opts.filename):
            this_key = row.pop(self.opts.key)
            self.annotations[this_key] = row

    def annotate_tree(self, t):
        for node in t.traverse():
            if node.name in self.annotations:
                for key, value in self.annotations[node.name].items():
                    node.add_feature(key, value)

    def extract_annotations(self, t, n):
        if self.opts.filename == "-" or not self.opts.filename:
            fp = sys.stdout  # pragma: no cover
        else:
            fp = open(self.opts.filename, "a" if n > 1 else "w")
        features = []
        for node in t.traverse():
            for f in node.features:
                if f not in ["dist", "support", "name"] and f not in features:
                    features.append(f)
        features.sort()
        fieldnames = ["name"]
        if self.opts.multiple:
            fieldnames.append("tree_number")
        fieldnames.extend(features)
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        if n == 1:
            writer.writeheader()
        for node in t.traverse():
            # Only include the root node or nodes with names
            if not node.name and node.up:
                continue
            if any([hasattr(node, f) for f in features]):
                if not node.name:
                    # Temporarily give the node a name
                    node.name = "root"
                    fix_root_name = True
                else:
                    fix_root_name = False
                rowdict = {f: getattr(node, f, "?") for f in fieldnames}
                if self.opts.multiple:
                    rowdict["tree_number"] = n
                writer.writerow(rowdict)
                if fix_root_name:
                    node.name = None
        if self.opts.filename and self.opts.filename != "-":
            fp.close()
