import sys
import types

class NewickFormatter:

    def __init__(self, out=sys.stdout, annotations=True):
        self.out = out
        self.annotations = annotations

    def consume(self, stream):
        first = True
        for t in stream:
            if first:
                first = False
                feature_names = set()
                for n in t.traverse():
                    feature_names |= n.features
                for standard_feature in ("dist", "name", "support"):
                    feature_names.remove(standard_feature)
            if self.annotations:
                self.out.write(t.write(features=feature_names,format_root_node=True))
            else:
                self.out.write(t.write())
            self.out.write("\n")

class NullSink:

    def __init__(self, out=sys.stdout):
        self.out = out

    def consume(self, stream):
        for t in stream:
            pass

class StringFormatter:

    def __init__(self, out=sys.stdout):
        self.out = out

    def consume(self, stream):
        for x in stream:
            if isinstance(x, types.StringTypes):
                self.out.write(x)
            else:
                try:
                    self.out.write("\n".join((str(element) for element in x)))
                except TypeError:
                    self.out.write(str(x))
            self.out.write("\n")

class ListPerLineFormatter:

    def __init__(self, out=sys.stdout):
        self.out = out

    def consume(self, stream):
        for lst in stream:
            self.out.write("\n".join(lst))


