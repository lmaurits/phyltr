import csv

from phyltr.commands.base import PhyltrCommand


class Rename(PhyltrCommand):
    """
    Rename the nodes in a treestream.  The mapping from old to new names is read
    from a file.
    """
    __options__ = [
        (
            ('-f', '--file'),
            dict(
                dest="filename",
                help='The filename of the translation file.  Each line of the translate file '
                     'should be of the format: "old:new"')),
        (
            ('--from',),
            dict(
                dest="from_", help='Column to lookup original taxa names.', default=None)),
        (
            ('--to',),
            dict(
                dest="to_", help='Column to lookup new taxa names.', default=None)),
        (
            ('-r', '--remove-missing'),
            dict(
                dest="remove", action="store_true", default=False,
                help='If there are taxa in the tree which are not in the translation file, remove '
                     'them (in the manner of subtree, not prune)')),
    ]

    def __init__(self, rename=None, **kw):
        PhyltrCommand.__init__(self, **kw)
        if rename:
            self.rename = rename
        elif self.opts.filename and self.opts.from_ and self.opts.to_:
            self.read_rename_file(self.opts.filename, self.opts.from_, self.opts.to_)
        else:
            raise ValueError("Must supply renaming dictionary or filename!")

    def read_rename_file(self, filename, old_column, new_column):

        """Read a file of names and their desired replacements and return a
        dictionary of this data."""

        rename = {}
        with open(filename, "r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                old = row[old_column]
                new = row[new_column]
                rename[old] = new
            fp.close()
        self.rename = rename

    def process_tree(self, t, n):
        # Rename nodes
        for node in t.traverse():
            new_name = self.rename.get(node.name, None)
            if new_name:
                node.name = new_name
            elif self.opts.remove:
                node.name = "KILL-THIS-NODE"

        keepers = [l for l in t.get_leaves() if l.name != "KILL-THIS-NODE"]
        if n == 1:
            self.pruning_needed = len(keepers) < len(t.get_leaves())

        if self.pruning_needed:
            mrca = t.get_common_ancestor(keepers)
            if t != mrca:
                t = mrca
            t.prune(keepers, preserve_branch_length=True)

        return t
