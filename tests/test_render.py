"""D2, ASCII and renderer failure handling."""

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.npm_graph.render import ascii_tree, render_svg, to_d2


class TestRender(unittest.TestCase):
    """Check complete graph representations without depending on live npm."""

    def test_d2_edges_and_isolated_nodes(self):
        """Use stable IDs and quoted labels for scoped names."""
        text = to_d2({'@scope/a': ['b'], 'b': [], 'alone': []})
        self.assertIn('n0: "@scope/a"', text)
        self.assertIn('n1: "alone"', text)
        self.assertIn('n0 -> n2', text)

    def test_d2_escapes(self):
        """Never interpolate a package label as executable D2 syntax."""
        self.assertIn('"a\\"b"', to_d2({'a"b': []}))

    def test_ascii_chain(self):
        """A simple tree uses plain ASCII connectors."""
        text = ascii_tree({'A': ['B'], 'B': ['C'], 'C': []}, 'A')
        self.assertEqual(text, 'A\n`-- B\n    `-- C')

    def test_ascii_cycle_and_shared(self):
        """Cycles and repeated subgraphs are explicit and finite."""
        graph = {'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['D'], 'D': []}
        text = ascii_tree(graph, 'A')
        self.assertIn('A [cycle]', text)
        self.assertIn('D [shared]', text)

    def test_missing_renderer(self):
        """Explain a missing D2 executable before creating output."""
        with patch('src.npm_graph.render.find_d2', return_value=None):
            with self.assertRaisesRegex(ValueError, 'D2'):
                render_svg({'A': []}, 'unused.svg')

    def test_failed_renderer_preserves_output(self):
        """A failed subprocess cannot destroy a previous successful image."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'graph.svg'
            output.write_text('old', encoding='utf-8')
            error = subprocess.CalledProcessError(1, ['d2'], stderr='bad D2')
            with patch('src.npm_graph.render.find_d2', return_value='d2'):
                with patch('subprocess.run', side_effect=error):
                    with self.assertRaisesRegex(ValueError, 'bad D2'):
                        render_svg({'A': []}, output)
            self.assertEqual(output.read_text(encoding='utf-8'), 'old')

    def test_success_writes_svg_and_d2(self):
        """Save both diagram source and validated SVG after rendering."""
        def fake_render(command, **kwargs):
            """Replace the external process with a tiny valid SVG output."""
            Path(command[-1]).write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')

        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'graph.svg'
            with patch('src.npm_graph.render.find_d2', return_value='d2'):
                with patch('subprocess.run', side_effect=fake_render):
                    render_svg({'A': []}, output)
            self.assertIn('<svg', output.read_text(encoding='utf-8'))
            self.assertIn('n0: "A"',
                          output.with_suffix('.d2').read_text(encoding='utf-8'))

    def test_renderer_timeout(self):
        """A hung D2 process gives a readable failure, not an endless wait."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'graph.svg'
            with patch('src.npm_graph.render.find_d2', return_value='d2'):
                with patch('subprocess.run',
                           side_effect=subprocess.TimeoutExpired('d2', 60)):
                    with self.assertRaisesRegex(ValueError, 'D2 output'):
                        render_svg({'A': []}, output)
            self.assertFalse(output.exists())

    def test_invalid_svg(self):
        """Successful exit alone does not prove SVG was created correctly."""
        def fake_render(command, **kwargs):
            """Create well-formed XML that is not SVG."""
            Path(command[-1]).write_text('<html/>', encoding='utf-8')

        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'graph.svg'
            with patch('src.npm_graph.render.find_d2', return_value='d2'):
                with patch('subprocess.run', side_effect=fake_render):
                    with self.assertRaisesRegex(ValueError, 'SVG document'):
                        render_svg({'A': []}, output)
