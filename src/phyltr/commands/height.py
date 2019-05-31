from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter


class Height(PhyltrCommand):
    """
    Print the heights of each tree in a stream.
    """
    sink = StringFormatter

    def process_tree(self, t, _):
        return t.get_farthest_leaf()[1]
