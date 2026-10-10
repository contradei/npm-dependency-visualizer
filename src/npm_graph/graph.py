"""Build a directed graph using recursive depth-first search."""


def build_graph(source, root, max_depth, exclude=''):
    """Visit names recursively, reopening nodes reached by shorter paths."""
    source.validate_root(root)
    if exclude and exclude in root:
        raise ValueError('exclude matches the root package')
    graph = {}
    best_depth = {}

    def visit(name, depth):
        """Expand one node if its remaining depth budget has improved."""
        graph.setdefault(name, [])
        if name in best_depth and best_depth[name] <= depth:
            return
        best_depth[name] = depth
        if depth >= max_depth:
            return
        children = sorted(child for child in source.dependencies(name)
                          if not exclude or exclude not in child)
        graph[name] = children
        for child in children:
            visit(child, depth + 1)

    visit(root, 0)
    return graph


def graph_lines(graph):
    """Represent edges and isolated/boundary nodes in stable order."""
    for name in sorted(graph):
        if not graph[name]:
            yield name
        for child in graph[name]:
            yield f'{name} -> {child}'


def load_order(graph):
    """Return DFS postorder and whether a strict topological order is absent."""
    active = set()
    done = set()
    order = []
    cyclic = False

    stack = [(name, False) for name in reversed(sorted(graph))]
    while stack:
        name, exiting = stack.pop()
        if exiting:
            active.remove(name)
            done.add(name)
            order.append(name)
        elif name in active:
            cyclic = True
        elif name not in done:
            active.add(name)
            stack.append((name, True))
            stack.extend((child, False)
                         for child in reversed(sorted(graph[name])))
    return order, cyclic
