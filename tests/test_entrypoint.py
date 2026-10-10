"""Check file and module invocation from real Python subprocesses."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TestEntrypoint(unittest.TestCase):
    """PyCharm's current-file launch must support relative package imports."""

    def test_direct_file_help_from_other_directory(self):
        """A direct script can display help regardless of the working folder."""
        script = Path('src/npm_graph/main.py').resolve()
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(script), '--help'],
                                    cwd=folder, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--package', result.stdout)

    def test_direct_file_missing_options(self):
        """Missing package is a normal CLI error, never an import traceback."""
        result = subprocess.run([sys.executable, 'src/npm_graph/main.py'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('--package', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_module_help(self):
        """Keep the documented module entry point working."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.npm_graph.main', '--help'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
