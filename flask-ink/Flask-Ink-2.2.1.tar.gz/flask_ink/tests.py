#!/usr/env/python
# -*- coding: utf-8 -*-

import unittest
import flask
import assets
import ink

class LocalAssetsTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = assets.LocalAssets()
        self.app = flask.Flask(__name__)

    def test_asset_url(self):
        with self.app.test_request_context('/page'):
            expected = '/static/ink/ink.css'
            actual = self.instance.asset_url('ink.css')
            self.assertEquals(expected, actual)


class ExternalLocationTestCase(unittest.TestCase):
    def setUp(self):
        self.external_location = assets.ExternalLocation('https://code.jquery.com/')

    def test_minified_filename(self):
        filename = 'afile.with.dots.js'
        self.assertEquals('afile.with.dots.min.js', self.external_location.minified_filename(filename))

        filename = 'afile_with_underscores.css'
        self.assertEquals('afile_with_underscores.min.css', self.external_location.minified_filename(filename))

    def test_compile_baseurl(self):
        self.external_location.tokens['custom_token'] = 'custom_value'
        self.external_location.tokens['test_token'] = 'ink_test'
        self.external_location.url_pattern = '{base_url}/{custom_token}?test_token={test_token}'

        expected_url = 'https://code.jquery.com/custom_value?test_token=ink_test'
        actual_url = self.external_location.compile_baseurl()
        self.assertEquals(expected_url, actual_url)

    def test_compile_baseurl_with_invalid_tokens(self):
        # Only the base_url and version tokens are available by default
        self.external_location.url_pattern = '{base_url}/{invalid_token}'

        with self.assertRaises(RuntimeError):
            self.external_location.compile_baseurl()

    def test_asset_url_minified_versioned(self):
        instance = assets.ExternalLocation('cdn.ink.sapo.pt')
        filename = 'demo.css'
        version = ink.__version__

        expected_url = '//cdn.ink.sapo.pt/demo.min.css?v='+version
        actual_url = instance.asset_url(filename, True, version)
        self.assertEquals(expected_url, actual_url)


class SapoCDNTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = assets.SapoCDN()

    def test_minified_filename(self):
        self.assertEquals('development-min.css', self.instance.minified_filename('development.css'))
        self.assertEquals('development.min.js', self.instance.minified_filename('development.js'))

    def test_asset_url(self):
        expected_url = '//cdn.ink.sapo.pt/1.0/application-min.css?v=1.0'
        actual_url = self.instance.asset_url('application.css', True, '1.0')

        self.assertEquals(expected_url, actual_url)


class AssetManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.instance = assets.AssetManager()
        self.local_asset = assets.LocalAssets()
        self.sapo_cdn = assets.SapoCDN()
        self.app = flask.Flask(__name__)

    def test_load_with_invalid_asset_location(self):
        self.instance.register_location('local', self.local_asset)

        with self.app.test_request_context('/page'):
            expected = '/static/ink/development.css'
            actual = self.instance.load('development.css', 'local')
            self.assertEquals(expected, actual)

            with self.assertRaises(assets.UnknownAssetLocationError):
                self.instance.load('development.css', 'sapo')


    def test_load_with_multiple_locations(self):
        self.instance.register_location('project', self.local_asset)
        self.instance.register_location('sapo', self.sapo_cdn)

        expected_project = '/static/ink/css/development.css'
        expected_sapo = '//cdn.ink.sapo.pt/'+ink.__version__+'/css/development.css'

        with self.app.test_request_context('/page'):
            self.assertEquals(expected_project, self.instance.load('css/development.css', 'project'))
            self.assertEquals(expected_sapo, self.instance.load('css/development.css', 'sapo'))


    def test_load_with_multiple_locations_minified(self):
        instance = assets.AssetManager(minified=True, asset_version='1.0')
        instance.register_location('local', self.local_asset)
        instance.register_location('sapo', self.sapo_cdn)

        expected_project = '/static/ink/css/development.min.css?v=1.0'
        expected_sapo = '//cdn.ink.sapo.pt/1.0/css/development-min.css?v=1.0'

        with self.app.test_request_context('/page'):
            self.assertEquals(expected_project, instance.load('css/development.css', 'local'))
            self.assertEquals(expected_sapo, instance.load('css/development.css', 'sapo'))


    def test_load_with_default_location(self):
        with self.assertRaises(assets.UnknownAssetLocationError):
            assets.AssetManager(minified=True, asset_version='10.0', default_location='local')

        instance = assets.AssetManager(minified=True, asset_version='10.0', location_map={'local': self.local_asset}, default_location='local')

        with self.app.test_request_context('/page'):
            expected_local = '/static/ink/css/development.min.css?v=10.0'
            self.assertEquals(expected_local, instance.load('css/development.css'))

            with self.assertRaises(assets.UnknownAssetLocationError):
                instance.load('css/development.css', 'sapo')


if __name__ == '__main__':
    unittest.main()
