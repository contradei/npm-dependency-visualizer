"""Stage 4: display dependency-first loading order."""

import sys

from .config import parse_args
from .fixtures import TestRepository
from .graph import build_graph, load_order
from .registry import NpmRepository


def main(argv=None):
    """Display DFS completion order and identify cycles explicitly."""
    args = parse_args(argv)
    try:
        source_type = TestRepository if args.test_mode else NpmRepository
        source = source_type(args.repository)
        graph = build_graph(source, args.package, args.max_depth, args.exclude)
        order, cyclic = load_order(graph)
        if cyclic:
            print('Cycle: no strict loading order; DFS completion order:')
        print(' -> '.join(order))
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
