"""Dependency-first DFS completion order."""

import unittest

from src.npm_graph.graph import load_order


class TestOrder(unittest.TestCase):
    """Check valid dependency order and honest cyclic-graph reporting."""

    def test_chain(self):
        """A dependency appears before its dependent."""
        order, cyclic = load_order({'A': ['B'], 'B': ['C'], 'C': []})
        self.assertEqual(order, ['C', 'B', 'A'])
        self.assertFalse(cyclic)

    def test_diamond(self):
        """Shared dependencies appear only once, before both parents."""
        graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}
        self.assertEqual(load_order(graph), (['D', 'B', 'C', 'A'], False))

    def test_cycle(self):
        """Report a cycle instead of claiming a topological order."""
        order, cyclic = load_order({'A': ['B'], 'B': ['A']})
        self.assertTrue(cyclic)
        self.assertEqual(set(order), {'A', 'B'})

    def test_isolated_nodes(self):
        """Handle standalone vertices deterministically."""
        self.assertEqual(load_order({'B': [], 'A': []}), (['A', 'B'], False))

    def test_long_path_with_short_root_distances(self):
        """Depth two can still produce paths exceeding the recursion limit."""
        names = [f'node_{index}' for index in range(1200)]
        graph = {name: [child] for name, child in zip(names, names[1:])}
        graph[names[-1]] = []
        graph['root'] = names
        order, cyclic = load_order(graph)
        self.assertFalse(cyclic)
        self.assertEqual(order, list(reversed(names)) + ['root'])
