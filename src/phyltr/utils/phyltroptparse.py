import collections
import statistics

from phyltr.utils.misc import read_taxa, DEFAULT

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


def taxa_spec_options(action):
    return TAXA_FILE_OPTIONS + [
        (
            ('taxa',),
            dict(
                metavar='TAXA', nargs='*',
                help="Leaf taxa in the tree to {0}".format(action),)),
        (
            ('-a', '--attribute'),
            dict(
                default=None,
                help='An attribute to inspect to decide which leaves to {0}. Must be used in '
                     'conjunction with --values.'.format(action))),
        (
            ('-v', '--values'),
            dict(
                default=None,
                help='A comma-separated list of values of the attribute specified with '
                     '--attribute, which specifies which taxa to {0}.'.format(action))),
    ]


def selector_from_taxa_spec(opts):
    """
    :param opts:
    :return: A callable which when passed a leaf returns True or False
    """
    if opts.taxa:
        pass
    elif opts.filename:
        opts.taxa = read_taxa(opts.filename, column=opts.column)

    inverse = getattr(opts, 'inverse', False)
    if opts.taxa:
        if inverse:
            return lambda l: l.name not in opts.taxa
        else:
            return lambda l: l.name in opts.taxa
    elif opts.attribute and opts.values:
        opts.values = opts.values.split(',')
        if inverse:
            return lambda l: getattr(l, opts.attribute, DEFAULT) not in opts.values
        else:
            return lambda l: getattr(l, opts.attribute, DEFAULT) in opts.values
    raise ValueError("Incompatible arguments")


def length_option(help):
    return (
        ('-l', '--lengths'),
        dict(
            action="store",
            dest="lengths",
            default=list(VALID_LENGTHS.keys())[0],
            choices=list(VALID_LENGTHS.keys()),
            help=help))
