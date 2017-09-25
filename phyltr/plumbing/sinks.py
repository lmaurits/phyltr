import types

class NewickFormatter:

    def __init__(self, out):
        self.out = out

    def consume(self, stream):
        for t in stream:
            self.out.write(t.write(features=[],format_root_node=True))
            self.out.write("\n")

class NullSink:

    def __init__(self, out):
        self.out = out

    def consume(self, stream):
        for t in stream:
            pass

class StringFormatter:

    def __init__(self, out):
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

    def __init__(self, out):
        self.out = out

    def consume(self, stream):
        for lst in stream:
            self.out.write("\n".join(lst))


