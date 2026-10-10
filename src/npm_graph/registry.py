"""Read npm metadata directly through the standard library."""

import json
from urllib.parse import quote
import urllib.request

from .config import npm_name


def extract_dependencies(metadata):
    """Validate latest-release metadata and return runtime declarations."""
    if not isinstance(metadata, dict):
        raise ValueError('metadata must be an object')
    if not isinstance(metadata.get('version'), str) or not metadata['version']:
        raise ValueError('metadata must contain a version string')
    dependencies = metadata.get('dependencies', {})
    if not isinstance(dependencies, dict):
        raise ValueError('dependencies must be an object')
    for name, version in dependencies.items():
        if not npm_name.fullmatch(name):
            raise ValueError(f'invalid dependency name: {name}')
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f'invalid dependency range: {name}')
    return dict(sorted(dependencies.items()))


class NpmRepository:
    """Cache the direct dependencies of the latest release of each name."""

    def __init__(self, url):
        """Keep an independent cache for a chosen registry."""
        self.url = url.rstrip('/')
        self.cache = {}

    def dependencies(self, name):
        """Fetch one latest-release document without npm or external clients."""
        if name not in self.cache:
            url = f'{self.url}/{quote(name, safe="")}/latest'
            request = urllib.request.Request(
                url, headers={'Accept': 'application/json',
                              'User-Agent': 'npm-graph-coursework/1.0'})
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    metadata = json.load(response)
                self.cache[name] = extract_dependencies(metadata)
            except (OSError, ValueError) as error:
                raise ValueError(f'Cannot read {name}: {error}') from error
        return dict(self.cache[name])

    def validate_root(self, name):
        """Check name syntax without fetching beyond a depth-zero boundary."""
        if not npm_name.fullmatch(name):
            raise ValueError('invalid npm package name')
