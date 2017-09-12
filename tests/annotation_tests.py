import csv
import fileinput
import tempfile

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.annotate import Annotate

def test_annotate():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated = Annotate("tests/argfiles/annotation.csv", "taxon").consume(trees)
    for t in annotated:
        t.write(features=[])
        for l in t.get_leaves():
            assert hasattr(l, "f1")
            assert hasattr(l, "f2")
            assert hasattr(l, "f3")

def test_extract_annotations():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    annotated = Annotate("tests/argfiles/annotation.csv", "taxon").consume(trees)
    with tempfile.NamedTemporaryFile() as fp:
        tempfilename = fp.name
        extracted = Annotate(tempfilename, extract=True).consume(annotated)
        list(extracted)
        lines.close()
        fp.seek(0)
        reader = csv.DictReader(fp)
        assert all((field in reader.fieldnames for field in ("f1","f2","f3")))
        for row in reader:
            if row["name"] == "A":
                assert row["f1"] == "0"
                assert row["f2"] == "1"
                assert row["f3"] == "1"
