"""Read small named test repositories from JSON adjacency lists."""

import json
from pathlib import Path

from .config import test_name


def validate_nodes(nodes):
    """Reject ambiguous shapes, invalid identifiers and dangling references."""
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError('test repository must be a nonempty JSON object')
    for name, children in nodes.items():
        if not test_name.fullmatch(name):
            raise ValueError('test package names must use A-Z')
        if not isinstance(children, list):
            raise ValueError(f'{name}: dependencies must be an array')
        for child in children:
            if not isinstance(child, str) or child not in nodes:
                raise ValueError(f'{name}: unknown dependency {child}')


class TestRepository:
    """A validated local repository with the same interface as npm."""

    def __init__(self, path):
        """Read and validate the entire repository before traversal."""
        nodes = json.loads(Path(path).read_text(encoding='utf-8'))
        validate_nodes(nodes)
        self.nodes = {name: sorted(set(children))
                      for name, children in nodes.items()}

    def validate_root(self, name):
        """Fail for missing packages even when analysis depth is zero."""
        if name not in self.nodes:
            raise ValueError(f'Unknown test package: {name}')

    def dependencies(self, name):
        """Return direct dependencies using placeholder version ranges."""
        self.validate_root(name)
        return dict.fromkeys(self.nodes[name], '*')
