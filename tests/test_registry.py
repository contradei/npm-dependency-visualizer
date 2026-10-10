"""Registry transport and metadata validation without live network tests."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src.npm_graph.registry import NpmRepository


class TestRegistry(unittest.TestCase):
    """Ensure only direct runtime dependencies are extracted."""

    def test_dependencies_and_cache(self):
        """Read scoped packages, retain ranges, and reuse downloaded data."""
        data = {'name': '@scope/demo', 'version': '1.0.0',
                'dependencies': {'other': '^2'},
                'devDependencies': {'dev': '*'}}
        with patch('urllib.request.urlopen',
                   return_value=io.BytesIO(json.dumps(data).encode())) as get:
            source = NpmRepository('https://registry.test/base/')
            expected = {'other': '^2'}
            self.assertEqual(source.dependencies('@scope/demo'), expected)
            self.assertEqual(source.dependencies('@scope/demo'), expected)
            self.assertEqual(get.call_count, 1)
            url = 'https://registry.test/base/%40scope%2Fdemo/latest'
            self.assertEqual(get.call_args.args[0].full_url, url)

    def test_leaf(self):
        """A package with no dependencies is a leaf."""
        with patch('urllib.request.urlopen',
                   return_value=io.BytesIO(b'{"version":"1.0.0"}')):
            self.assertEqual(NpmRepository('https://r').dependencies('a'), {})

    def test_bad_metadata(self):
        """Reject invalid JSON, types, dependency names and ranges."""
        values = [b'not json', b'[]', b'{}', b'{"version": 2}',
                  b'{"version":"1", "dependencies": []}',
                  b'{"version":"1", "dependencies": {"bad/name":"*"}}',
                  b'{"version":"1", "dependencies": {"a":2}}']
        for value in values:
            with self.subTest(value=value):
                with patch('urllib.request.urlopen',
                           return_value=io.BytesIO(value)):
                    with self.assertRaises(ValueError):
                        NpmRepository('https://r').dependencies('a')

    def test_transport_errors(self):
        """Convert HTTP, connection and timeout failures into clear errors."""
        errors = [HTTPError('https://r/a', 404, 'missing', {}, None),
                  URLError('offline'), TimeoutError('timeout')]
        for error in errors:
            with self.subTest(error=error):
                with patch('urllib.request.urlopen', side_effect=error):
                    with self.assertRaisesRegex(ValueError, 'Cannot read a'):
                        NpmRepository('https://r').dependencies('a')
