"""Validate the seven command-line settings."""

import argparse
from pathlib import Path
import re
from urllib.parse import urlsplit


max_depth_limit = 200
min_depth = 0
npm_name = re.compile(r'(?:@[a-z0-9._-]+/)?[a-z0-9][a-z0-9._-]*\Z')
test_name = re.compile(r'[A-Z]+\Z')


def depth_value(value):
    """Parse a depth that remains within Python's recursion budget."""
    try:
        depth = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError('depth must be an integer') from error
    if not min_depth <= depth <= max_depth_limit:
        raise argparse.ArgumentTypeError('depth must be between 0 and 200')
    return depth


def validate_repository(args):
    """Require a readable test file or an HTTP(S) registry base URL."""
    if args.test_mode:
        if not Path(args.repository).is_file():
            raise ValueError('test repository must be an existing file')
        with Path(args.repository).open('rb') as stream:
            stream.read(1)
        return
    validate_url(args.repository)


def validate_url(repository):
    """Check HTTP URL syntax, credentials, query, fragment and port."""
    url = urlsplit(repository)
    if url.scheme not in ('http', 'https') or not url.hostname:
        raise ValueError('repository must be an HTTP(S) URL')
    if url.username or url.password or url.query or url.fragment:
        raise ValueError('repository URL cannot contain credentials/query/hash')
    if any(char.isspace() for char in repository):
        raise ValueError('repository URL cannot contain whitespace')
    if url.port is not None:
        int(url.port)


def validate_settings(args):
    """Validate names and output without creating files during parsing."""
    pattern = test_name if args.test_mode else npm_name
    if not pattern.fullmatch(args.package):
        raise ValueError('invalid package name for the selected mode')
    validate_repository(args)
    if args.exclude and not args.exclude.strip():
        raise ValueError('exclude cannot contain only whitespace')
    if args.exclude and args.exclude in args.package:
        raise ValueError('exclude matches the root package')
    validate_output(args)


def validate_output(args):
    """Prevent invalid destinations and overwriting the input file."""
    output = Path(args.output)
    if output.suffix.lower() != '.svg' or not output.parent.is_dir():
        raise ValueError('output needs .svg extension and an existing parent')
    if output.is_dir():
        raise ValueError('output cannot be a directory')
    if args.test_mode:
        source = Path(args.repository).resolve()
        if source in (output.resolve(), output.with_suffix('.d2').resolve()):
            raise ValueError('output cannot replace the test repository')


def parse_args(argv=None):
    """Return checked configuration or argparse's user-facing error."""
    parser = argparse.ArgumentParser(description='npm dependency graph')
    parser.add_argument('--package', required=True, help='npm name / A-Z')
    parser.add_argument('--repository', default='https://registry.npmjs.org',
                        help='registry base URL or test JSON path')
    parser.add_argument('--test-mode', action='store_true', help='use JSON')
    parser.add_argument('--output', default='graph.svg', help='SVG file name')
    parser.add_argument('--ascii', action='store_true', help='show ASCII tree')
    parser.add_argument('--max-depth', type=depth_value, default=5,
                        help='0=root, 1=direct; range 0..200, default 5')
    parser.add_argument('--exclude', default='', help='exclude name substring')
    args = parser.parse_args(argv)
    try:
        validate_settings(args)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return args
