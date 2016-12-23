#! /usr/bin/python

"""
This code is dirty
command-line script
TODO : make it work
"""

"""
arguments :
- package to patch (default to '')
- log file (default to stdout)
- file to execute (no default)
- blacklist (default to [])
"""


def do():
    """not working yet, don't try to use it."""

    import argparse
    from logme import hook_imports

    parser = argparse.ArgumentParser(
        description='logging of ALL caught exceptions')

    parser.add_argument('-in', '--required', nargs='+', dest='required',
                        help="the name of the package you want to patch")

    parser.add_argument('-ex', '--exclude', nargs='*',
                        default=[], dest='exclude',
                        help="the files you don't want to patch")

    # TODO : add default for Windows
    parser.add_argument('-lf', '--log_file', nargs='?',
                        default='/dev/stdout', dest='log_file',
                        help='the file you want to log exceptions in')

    parser.add_argument('executable_file', nargs=1,
                        help="your python app entry point")

    args = parser.parse_args()

    # AND NOW ?

    hook_imports(log_file=args.log_file, required=args.include, exclude=args.exclude, packaged=False)
