"""Stage 3: recursively build dependency graphs from npm or test JSON."""

import sys

from .config import parse_args
from .fixtures import TestRepository
from .graph import build_graph, graph_lines
from .registry import NpmRepository


def main(argv=None):
    """Display graph edges and report failures without a traceback."""
    args = parse_args(argv)
    try:
        source_type = TestRepository if args.test_mode else NpmRepository
        source = source_type(args.repository)
        graph = build_graph(source, args.package, args.max_depth, args.exclude)
        print('\n'.join(graph_lines(graph)))
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
