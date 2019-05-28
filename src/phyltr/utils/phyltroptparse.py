import collections
try:
    import statistics
except ImportError:  # pragma: no cover
    from backports import statistics

TAXA_FILE_OPTIONS = [
    (
        ('-f', '--file'), dict(dest="filename", help='Specifies a file from which to read taxa')),
    (
        ('--column',),
        dict(
            dest="column", default=None,
            help='Specifies a column in the CSV file from which to read taxa')),
]
VALID_LENGTHS = collections.OrderedDict([
    ("mean", statistics.mean),
    ("max", max),
    ("min", min),
    ("median", statistics.median)])

def length_option(help):
    return (
        ('-l', '--lengths'),
        dict(
            action="store",
            dest="lengths",
            default=list(VALID_LENGTHS.keys())[0],
            choices=list(VALID_LENGTHS.keys()),
            help=help))
