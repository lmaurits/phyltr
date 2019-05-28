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
                dest="remove",action="store_true", default=False,
                help='If there are taxa in the tree which are not in the translation file, remove '
                     'them (in the manner of subtree, not prune)')),
    ]

    def __init__(self, rename=None, **kw):
        PhyltrCommand.__init__(self, **kw)
        if rename:
            self.rename = rename
        elif self.opts.filename:
            self.read_rename_file(self.opts.filename)
        else:
            raise ValueError("Must supply renaming dictionary or filename!")
        self.first = True

    @classmethod 
    def init_from_opts(cls, options, files):
        return cls(filename=options.filename, remove=options.remove)

    def read_rename_file(self, filename):

        """Read a file of names and their desired replacements and return a
        dictionary of this data."""

        rename = {}
        with open(filename, "r") as fp:
            for line in fp:
                old, new = line.strip().split(":")
                old = ",".join((x.strip() for x in old.split(",")))
                new = new.strip()
                rename[old] = new
            fp.close()
        self.rename = rename

    def process_tree(self, t):
        # Rename nodes
        for node in t.traverse():
            node.name = self.rename.get(node.name,
                    "KILL-THIS-NODE" if self.opts.remove else node.name)

        keepers = [l for l in t.get_leaves() if l.name != "KILL-THIS-NODE"]
        if self.first:
            n_leaves = len(t.get_leaves())
            self.pruning_needed = len(keepers) < n_leaves
            self.first = False

        if self.pruning_needed:
            mrca = t.get_common_ancestor(keepers)
            if t != mrca:
                t = mrca
            t.prune(keepers, preserve_branch_length=True)

        return t
