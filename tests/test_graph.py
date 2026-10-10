"""Recursive DFS, depth limits, pruning, cycles and test repositories."""

import json
from pathlib import Path
import tempfile
import unittest

from src.npm_graph.fixtures import TestRepository
from src.npm_graph.graph import build_graph


def fixture_source(nodes):
    """Build a checked in-memory fixture using the real JSON reader."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'repo.json'
        path.write_text(json.dumps(nodes), encoding='utf-8')
        return TestRepository(path)


class TestGraph(unittest.TestCase):
    """Exercise graph topology rather than implementation details."""

    def test_chain_and_depth(self):
        """Include boundary nodes but do not traverse beyond them."""
        source = fixture_source({'A': ['B'], 'B': ['C'], 'C': []})
        self.assertEqual(build_graph(source, 'A', 0), {'A': []})
        self.assertEqual(build_graph(source, 'A', 1), {'A': ['B'], 'B': []})
        self.assertEqual(build_graph(source, 'A', 2), source.nodes)

    def test_cycle(self):
        """Preserve the closing edge of a cycle and terminate."""
        nodes = {'A': ['B'], 'B': ['A']}
        self.assertEqual(build_graph(fixture_source(nodes), 'A', 20), nodes)

    def test_self_cycle(self):
        """A self-dependency is represented once."""
        self.assertEqual(build_graph(fixture_source({'A': ['A']}), 'A', 5),
                         {'A': ['A']})

    def test_shorter_path_reopens_depth_budget(self):
        """A shared node reached later by a shorter path expands further."""
        nodes = {'A': ['B', 'D'], 'B': ['C'], 'C': ['D'],
                 'D': ['E'], 'E': ['F'], 'F': []}
        graph = build_graph(fixture_source(nodes), 'A', 3)
        self.assertEqual(graph['E'], ['F'])
        self.assertIn('F', graph)

    def test_filter_prunes_subtree(self):
        """Excluded names and their exclusively reachable children disappear."""
        nodes = {'A': ['B', 'C'], 'B': ['D'], 'C': [], 'D': []}
        graph = build_graph(fixture_source(nodes), 'A', 5, 'B')
        self.assertEqual(graph, {'A': ['C'], 'C': []})

    def test_unknown_root(self):
        """Unknown fixture roots are errors even at depth zero."""
        with self.assertRaises(ValueError):
            build_graph(fixture_source({'A': []}), 'Z', 0)

    def test_invalid_fixtures(self):
        """Reject malformed shapes, lowercase names and dangling edges."""
        for nodes in ([], {}, {'a': []}, {'A': 'B'}, {'A': ['B']},
                      {'A': [1]}, {'A': [], 'B': None}):
            with self.subTest(nodes=nodes):
                with self.assertRaises(ValueError):
                    fixture_source(nodes)

    def test_broken_json(self):
        """Malformed test files cannot be mistaken for an empty graph."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.json'
            path.write_text('{', encoding='utf-8')
            with self.assertRaises(ValueError):
                TestRepository(path)

    def test_root_filter(self):
        """Do not silently show a root that the user excluded."""
        with self.assertRaises(ValueError):
            build_graph(fixture_source({'A': []}), 'A', 2, 'A')
