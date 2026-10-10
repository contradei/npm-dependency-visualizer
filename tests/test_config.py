"""CLI configuration and errors for every user option."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.npm_graph.config import parse_args
from src.npm_graph.main import main


class TestConfig(unittest.TestCase):
    """Check defaults, all options, and invalid user inputs."""

    def test_defaults(self):
        """Use the public registry and a bounded default analysis."""
        args = parse_args(['--package', 'is-odd'])
        self.assertEqual(args.repository, 'https://registry.npmjs.org')
        self.assertEqual(args.max_depth, 5)
        self.assertFalse(args.ascii)
        self.assertFalse(args.test_mode)
        self.assertEqual(args.exclude, '')

    def test_all_options(self):
        """Keep all seven configuration options in the namespace."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'graph.json'
            path.write_text('{"A": []}', encoding='utf-8')
            args = parse_args([
                '--package', 'A', '--repository', str(path), '--test-mode',
                '--output', str(Path(folder) / 'out.svg'), '--ascii',
                '--max-depth', '0', '--exclude', 'B',
            ])
            self.assertEqual(args.package, 'A')
            self.assertTrue(args.ascii)
            self.assertEqual(args.max_depth, 0)

    def test_invalid_options(self):
        """Every parameter rejects invalid values with a usage error."""
        cases = [
            [], ['--package', ''], ['--package', 'UPPER'],
            ['--package', '../bad'], ['--repository', 'ftp://host'],
            ['--repository', 'https://'], ['--repository', 'https://a:bad'],
            ['--repository', 'https://user:pass@host'],
            ['--repository', 'https://host/?q=1'],
            ['--repository', 'https://host/#x'],
            ['--test-mode', 'false'], ['--ascii', 'false'],
            ['--test-mode'], ['--output', ''], ['--output', 'out.png'],
            ['--output', 'missing-parent/out.svg'],
            ['--max-depth', '-1'], ['--max-depth', 'word'],
            ['--max-depth', '201'], ['--exclude', ' '],
            ['--exclude', 'is-odd'], ['--unknown'],
        ]
        for options in cases:
            with self.subTest(options=options):
                argv = ['--package', 'is-odd'] + options if options else []
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as caught:
                        parse_args(argv)
                self.assertEqual(caught.exception.code, 2)

    def test_scoped_name(self):
        """Accept normal scoped npm names."""
        self.assertEqual(parse_args(['--package', '@types/node']).package,
                         '@types/node')

    def test_order_output(self):
        """Stage four prints dependencies before their parent."""
        output = io.StringIO()
        with patch('src.npm_graph.registry.NpmRepository.dependencies',
                   return_value={'is-number': '^6.0.0'}):
            with contextlib.redirect_stdout(output):
                result = main(['--package', 'is-odd', '--max-depth', '1'])
        self.assertEqual(result, 0)
        self.assertIn('is-number -> is-odd', output.getvalue())
