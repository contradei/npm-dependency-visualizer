"""Generate D2 source, SVG images and finite ASCII trees."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.etree.ElementTree import ParseError, parse


def to_d2(graph):
    """Use stable synthetic IDs and JSON-quoted labels in D2 syntax."""
    names = {name: f'n{index}' for index, name in enumerate(sorted(graph))}
    lines = ['direction: down']
    for name, identifier in names.items():
        lines.append(f'{identifier}: {json.dumps(name)}')
    for name in sorted(graph):
        for child in sorted(graph[name]):
            lines.append(f'{names[name]} -> {names[child]}')
    return '\n'.join(lines) + '\n'


def ascii_tree(graph, root):
    """Display repeated nodes once and distinguish shared nodes from cycles."""
    lines = []
    expanded = set()
    stack = [(root, '', '', frozenset())]
    while stack:
        name, prefix, branch, ancestors = stack.pop()
        suffix = node_marker(name, ancestors, expanded)
        lines.append(prefix + branch + name + suffix)
        if suffix:
            continue
        expanded.add(name)
        child_prefix = prefix
        if branch:
            child_prefix += '    ' if branch == '`-- ' else '|   '
        children = sorted(graph[name])
        for child in reversed(children):
            connector = '`-- ' if child == children[-1] else '+-- '
            stack.append((child, child_prefix, connector, ancestors | {name}))
    return '\n'.join(lines)


def node_marker(name, ancestors, expanded):
    """Select a truthful marker for an already encountered vertex."""
    if name in ancestors:
        return ' [cycle]'
    if name in expanded:
        return ' [shared]'
    return ''


def find_d2():
    """Prefer the project-local renderer, otherwise search PATH."""
    local = Path(__file__).resolve().parents[2] / 'tools' / 'd2.exe'
    return str(local) if local.is_file() else shutil.which('d2')


def run_renderer(executable, source, destination):
    """Bound renderer execution and validate the resulting SVG document."""
    command = [executable, '--layout=dagre', str(source), str(destination)]
    try:
        subprocess.run(command, check=True, capture_output=True,
                       text=True, encoding='utf-8', errors='replace',
                       timeout=60)
        root = parse(destination).getroot()
        if root.tag != '{http://www.w3.org/2000/svg}svg':
            raise ValueError('D2 did not produce an SVG document')
    except subprocess.CalledProcessError as error:
        raise ValueError(f'D2 failed: {error.stderr.strip()}') from error
    except (subprocess.TimeoutExpired, ParseError) as error:
        raise ValueError(f'D2 output failed: {error}') from error


def render_svg(graph, output):
    """Render in a temporary directory before publishing successful files."""
    executable = find_d2()
    if not executable:
        raise ValueError('D2 not found: install d2 or put it in tools/d2.exe')
    destination = Path(output).resolve()
    with tempfile.TemporaryDirectory(dir=destination.parent) as folder:
        source = Path(folder) / 'graph.d2'
        result = Path(folder) / 'graph.svg'
        source.write_text(to_d2(graph), encoding='utf-8')
        run_renderer(executable, source, result)
        source.replace(destination.with_suffix('.d2'))
        result.replace(destination)
