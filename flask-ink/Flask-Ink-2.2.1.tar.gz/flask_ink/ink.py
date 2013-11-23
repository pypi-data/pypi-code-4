#!/usr/env/python
# -*- coding: utf-8 -*-

import flask
import assets

__version__ = '2.2.1'

class Ink(object):
    def __init__(self, app):
        self.app = app
        self.init_app()

    def init_app(self):
        self.app.config.setdefault('INK_MINIFIED_ASSETS', False);
        self.app.config.setdefault('INK_VERSION', __version__)
        self.app.config.setdefault('INK_DEFAULT_ASSET_LOCATION', 'sapo')

        minified_assets = self.app.config['INK_MINIFIED_ASSETS']
        asset_version = self.app.config['INK_VERSION']
        asset_location = self.app.config['INK_DEFAULT_ASSET_LOCATION']

        self.assets = assets.AssetManager(minified=minified_assets, asset_version=asset_version)
        self.make_default_asset_locations()
        self.assets.default_location = asset_location

        blueprint = flask.Blueprint(
            'ink',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=self.app.static_url_path+'/ink')

        self.app.register_blueprint(blueprint)
        self.app.jinja_env.globals.update(ink_load_asset=self.assets.load)

    def make_default_asset_locations(self):
        sapo = assets.SapoCDN()
        local = assets.LocalAssets()

        self.assets.register_location('sapo', sapo)
        self.assets.register_location('local', local)
