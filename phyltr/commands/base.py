class PhyltrCommand:

    def consume(self, stream):
        for tree in stream:
            try:
                res = self.process_tree(tree)
                if res:
                    yield res
            except StopIteration:
                stream.close()
                break
        for tree in self.postprocess():
            yield tree

    def process_tree(self, t):
        return t    # pragma: no cover

    def postprocess(self):
        return []
