import logging

from deployer.deployment import Deployment
from deployer.config import ConfigStack
from deployer.utils import ErrorExit

from .base import Base


class ConfigTest(Base):

    def setUp(self):
        self.output = self.capture_logging(
            "deployer.config", level=logging.DEBUG)

    def test_config_basic(self):
        config = ConfigStack(['configs/ostack-testing-sample.cfg'])
        config.load()
        self.assertEqual(
            config.keys(),
            [u'openstack-precise-ec2',
             u'openstack-precise-ec2-trunk',
             u'openstack-ubuntu-testing'])
        self.assertRaises(ErrorExit, config.get, 'zeeland')
        result = config.get("openstack-precise-ec2")
        self.assertTrue(isinstance(result, Deployment))

    def test_config(self):
        config = ConfigStack([
            "test_data/stack-default.cfg", "test_data/stack-inherits.cfg"])
        config.load()
        self.assertEqual(
            config.keys(),
            [u'my-files-frontend-dev', u'wordpress'])
        deployment = config.get("wordpress")
        self.assertTrue(deployment)


class NetworkConfigFetchingTests(Base):
    """Configuration files can be specified via URL that is then fetched."""

    def setUp(self):
        self.output = self.capture_logging(
            "deployer.config", level=logging.DEBUG)

    def test_urls_are_fetched(self):
        # If a config file is specified as a URL, that URL is fetched and
        # placed at a temporary location where it is read and treated as a
        # regular config file.
        CONFIG_URL = 'http://site.invalid/config-1'
        config = ConfigStack([])
        config.config_files = [CONFIG_URL]

        class FauxResponse(file):
            def getcode(self):
                return 200

        def faux_urlopen(url):
            self.assertEqual(url, CONFIG_URL)
            return FauxResponse('configs/ostack-testing-sample.cfg')

        config.load(urlopen=faux_urlopen)
        self.assertEqual(
            config.keys(),
            [u'openstack-precise-ec2',
             u'openstack-precise-ec2-trunk',
             u'openstack-ubuntu-testing'])
        self.assertRaises(ErrorExit, config.get, 'zeeland')
        result = config.get("openstack-precise-ec2")
        self.assertTrue(isinstance(result, Deployment))

    def test_unfetchable_urls_generate_an_error(self):
        # If a config file is specified as a URL, that URL is fetched and
        # placed at a temporary location where it is read and treated as a
        # regular config file.
        CONFIG_URL = 'http://site.invalid/config-1'
        config = ConfigStack([])
        config.config_files = [CONFIG_URL]

        class FauxResponse(file):
            def getcode(self):
                return 400

        def faux_urlopen(url):
            self.assertEqual(url, CONFIG_URL)
            return FauxResponse('configs/ostack-testing-sample.cfg')
        self.assertRaises(ErrorExit, config.load, urlopen=faux_urlopen)
