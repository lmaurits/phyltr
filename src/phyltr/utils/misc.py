import csv


class Default(object):
    def __eq__(self, other):
        return False

DEFAULT = Default()


def dicts_from_csv(fname):
    with open(fname, "r") as fp:
        dialect = csv.Sniffer().sniff(fp.read(1024))
        fp.seek(0)
        return list(csv.DictReader(fp, dialect=dialect))


def read_taxa(taxa=None, filename=None, column=None):
    if taxa:
        return taxa
    if filename:
        if column:
            return set(d[column] for d in dicts_from_csv(filename))
        with open(filename, "r") as fp:
            res = set([t.strip() for t in fp.readlines()])
        if not res:
            raise ValueError("Empty file!")
        return res
