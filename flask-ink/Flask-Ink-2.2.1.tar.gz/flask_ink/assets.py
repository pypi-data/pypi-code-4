#!/usr/env/python
# -*- coding: utf-8 -*-

import re
import flask
import ink

class AssetLocation(object):
    """Abstractly represents a location from where your static files
    get served from.

    """
    def asset_url(self, filename, minified=False, version=None):
        """Responsible for translating a filename into a complete valid URL
        pointing to that particular resource.

        Args:
            filename (str): relative path to the file (ex. css/development.css)
            minified (bool): if true, should point out a minified version of the file
            version (int): if not none, should return a version for the file

        """
        raise NotImplementedError

    def minified_filename(self, filename):
        """Returns the expected minified filename for the asset.
        Ex. css/development.css -> css/development.min.css

        """
        return '%s.min.%s' % tuple(filename.rsplit('.', 1))

    def versioned_filename(self, filename, version):
        if type(version) is bool:
            version = __version__

        return filename+'?v='+version


class LocalAssets(AssetLocation):
    """Represents assets served locally. Uses flask's url_for to determine
    the resource's location.

    """
    def __init__(self, directory='static', prefix='ink'):
        self.directory = directory
        self.prefix = prefix

    def asset_url(self, filename, minified=False, version=None):
        filename = self.minified_filename(filename) if minified else filename
        filename = self.prefix+"/{0}".format(filename)

        params = {'filename': filename}

        if version:
            params['v'] = version

        return flask.url_for(self.directory, **params)


class ExternalLocation(AssetLocation):
    """Represents assets that are located *somewhere* externally (like a CDN for
    instance

    """
    def __init__(self, base_url, url_pattern="//{base_url}", tokens = {}):
        """Constructor

        Args:
            base_url (str): The url hostname from where the resources will be served (ex. cdn.jquery.org)
            url_pattern (str): To flexibilize a bit the way the final asset url is build, you can define how it will
                get built. //{base_url}, would yield //cdn.jquery.org/myfile.js as a result
            tokens (dict): A dictionary of tokens that may be used to build the url_pattern

        """
        self.base_url = base_url.rstrip('/')
        self.url_pattern = url_pattern.rstrip('/')

        tokens['base_url'] = self.base_url
        self.tokens = tokens

    def compile_baseurl(self, version=None):
        regex = re.compile('\{(\w+)\}')
        tokens = regex.findall(self.url_pattern)
        known_tokens = self.tokens

        version = version or ink.__version__
        known_tokens['version'] = version

        unknown_tokens = set(tokens) - set(known_tokens)

        if len(unknown_tokens):
            raise RuntimeError("Unknown tokens on your url_pattern: {}".format(unknown_tokens))

        return self.url_pattern.format(**known_tokens)


    def asset_url(self, filename, minified=False, version=None):
        filename = self.minified_filename(filename) if minified else filename
        filename = self.versioned_filename(filename, version) if version else filename

        base_url = self.compile_baseurl(version)
        base_url += '/'+filename

        return base_url


class SapoCDN(ExternalLocation):
    """Specializes the ExternalLocation and adds direct support to Sapo's Ink CDN.

    """
    def __init__(self, tokens = {}):
        base_url = 'cdn.ink.sapo.pt'
        url_pattern = '//{base_url}/{version}'

        super(SapoCDN, self).__init__(base_url, url_pattern, tokens)

    def minified_filename(self, filename):
        filename_parts = filename.rsplit('.', 1)
        extension = filename_parts[1]

        pattern = '%s-min.%s' if filename_parts[1] == 'css' else '%s.min.%s'
        return pattern % tuple(filename_parts)


class AssetManager(object):
    """Is responsible for storing the available AssetLocation's available and for dispatching
    to one of the registered instances, the requests for actually generating an URL for a resource.

    """
    def __init__(
        self, location_map={}, minified=False, asset_version=None,
        default_location=None):
        """Constructor

        Args:
        location_map (dict): An hash with the default AssetLocation instances available
        minified (bool): If true, the minified version of the resources are returned
        asset_version (str): The default version of the assets to be returned
        default_location (str): The default location used, when is asked for the instance to get an URL
            for a resource
        """

        self.location_map = location_map
        self.minified = minified
        self.asset_version = asset_version
        self.default_location = default_location

        # Make sure we have a valid default location, as the get_location_by_name method
        # raises an error if it isn't registered
        if self.default_location is not None:
            self.get_location_by_name(self.default_location)

    def load(self, filename, location=None):
        """ Gets an URL for a static asset. Delegates the actual URL building logic to the AssetLocation instance
        pointed by the 'location' argument.

        """
        location = location or self.default_location
        location_instance = self.get_location_by_name(location)

        filename = filename.strip('/')
        return location_instance.asset_url(filename, self.minified, self.asset_version)

    def get_location_by_name(self, name):
        if name in self.location_map:
            return self.location_map[name]

        name = '' if type(name) != str else name
        raise UnknownAssetLocationError("Unkown location instance "+name)


    def register_location(self, name, location):
        self.location_map[name] = location


class UnknownAssetLocationError(RuntimeError):
    pass
