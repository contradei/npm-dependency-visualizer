"""Stage 1: print validated command-line configuration."""

from .config import parse_args


def main(argv=None):
    """Print each user setting and return success."""
    args = parse_args(argv)
    for name, value in vars(args).items():
        print(f'{name}={value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
