"""Stage 5: render npm or test dependency graphs as D2, SVG and ASCII."""

from pathlib import Path
import sys

if __package__:
    from .config import parse_args
    from .fixtures import TestRepository
    from .graph import build_graph
    from .registry import NpmRepository
    from .render import ascii_tree, render_svg
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.npm_graph.config import parse_args
    from src.npm_graph.fixtures import TestRepository
    from src.npm_graph.graph import build_graph
    from src.npm_graph.registry import NpmRepository
    from src.npm_graph.render import ascii_tree, render_svg


def main(argv=None):
    """Save a diagram and optionally display its ASCII representation."""
    args = parse_args(argv)
    try:
        source_type = TestRepository if args.test_mode else NpmRepository
        source = source_type(args.repository)
        graph = build_graph(source, args.package, args.max_depth, args.exclude)
        render_svg(graph, args.output)
        print(f'SVG: {args.output}')
        if args.ascii:
            print(ascii_tree(graph, args.package))
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
