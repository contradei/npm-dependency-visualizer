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
