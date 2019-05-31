from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import ListPerLineFormatter


class Taxa(PhyltrCommand):
    """
    Extract the taxa names from the first tree in a stream.
    """
    sink = ListPerLineFormatter

    def process_tree(self, t, n):
        if n > 1:
            raise StopIteration
        return sorted([n.name for n in t.traverse() if n.name])
