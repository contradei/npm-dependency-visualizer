"""Stage 2: display direct runtime dependencies from npm."""

import sys

from .config import parse_args
from .registry import NpmRepository


def main(argv=None):
    """Print direct dependencies, reporting source failures in stderr."""
    args = parse_args(argv)
    try:
        if args.test_mode:
            raise ValueError('test graph mode is introduced in stage 3')
        dependencies = NpmRepository(args.repository).dependencies(args.package)
        for name, version in dependencies.items():
            print(f'{name} {version}')
        if not dependencies:
            print('(no direct dependencies)')
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
