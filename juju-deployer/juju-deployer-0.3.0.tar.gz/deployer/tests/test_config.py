import logging
import os
import tempfile
import yaml

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
            os.path.join(self.test_data_dir, "stack-default.cfg"),
            os.path.join(self.test_data_dir, "stack-inherits.cfg")])
        config.load()
        self.assertEqual(
            config.keys(),
            [u'my-files-frontend-dev', u'wordpress'])
        deployment = config.get("wordpress")
        self.assertTrue(deployment)

    def test_config_include_file(self):
        config = ConfigStack([
            os.path.join(self.test_data_dir, "stack-includes.cfg")])
        config.load()
        # ensure picked up stacks from both files
        self.assertEqual(
            config.keys(),
            [u'my-files-frontend-dev', u'wordpress'])

        # ensure inheritance was adhered to during cross-file load
        wordpress = [s.name for s in config.get('wordpress').get_services()]
        my_app = [s.name for s in
                  config.get('my-files-frontend-dev').get_services()]
        self.assertTrue(set(wordpress).issubset(set(my_app)))

    def test_inherits_config_overridden(self):
        config = ConfigStack([
            os.path.join(self.test_data_dir, "stack-default.cfg"),
            os.path.join(self.test_data_dir, "stack-inherits.cfg")])
        config.load()
        deployment = config.get('my-files-frontend-dev')
        db = deployment.get_service('db')
        # base deployment (wordpress)'s db tuning level should have been
        # over-ridden
        self.assertEquals(db.config.get('tuning-level'), 'fastest')

    def test_multi_inheritance_multi_files(self):
        config = ConfigStack([
            os.path.join(self.test_data_dir, "openstack", "openstack.cfg"),
            os.path.join(self.test_data_dir, "openstack", "ubuntu_base.cfg"),
            os.path.join(
                self.test_data_dir, "openstack", "openstack_base.cfg"),
        ])
        self._test_multiple_inheritance(config)

    def test_multi_inheritance_multi_included_files(self):
        # openstack.cfg
        #  includes -> ubuntu_base.cfg includes
        #               includes -> openstack_base.cfg
        test_conf = yaml.load(open(
            os.path.join(self.test_data_dir, "openstack", "openstack.cfg")))
        includes = [
            os.path.join(self.test_data_dir, "openstack", "ubuntu_base.cfg"),
            os.path.join(self.test_data_dir, "openstack", "openstack_base.cfg")
        ]
        for key in ['include-config', 'include-configs']:
            test_conf[key] = includes
            with tempfile.NamedTemporaryFile() as tmp_cfg:
                tmp_cfg.write(yaml.dump(test_conf))
                tmp_cfg.flush()
                config = ConfigStack([tmp_cfg.name])
                self._test_multiple_inheritance(config)
            del test_conf[key]

    def test_multi_inheritance_included_multi_configs(self):
        # openstack.cfg
        #  includes -> [ubuntu_base.cfg, openstack_base.cfg]
        config = ConfigStack([
            os.path.join(self.test_data_dir, "openstack", "openstack.cfg"),
        ])
        self._test_multiple_inheritance(config)

    def _test_multiple_inheritance(self, config):
        config.load()

        deployment = config.get('precise-grizzly')
        services = [s.name for s in list(deployment.get_services())]
        self.assertEquals(['mysql', 'nova-cloud-controller'], services)

        nova = deployment.get_service('nova-cloud-controller')
        self.assertEquals(nova.config['openstack-origin'],
                          'cloud:precise-grizzly')

        deployment = config.get('precise-grizzly-quantum')
        services = [s.name for s in list(deployment.get_services())]
        self.assertEquals(services,
                          ['mysql', 'nova-cloud-controller',
                           'quantum-gateway'])
        nova = deployment.get_service('nova-cloud-controller')
        self.assertEquals(nova.config['network-manager'], 'Quantum')
        self.assertEquals(nova.config['openstack-origin'],
                          'cloud:precise-grizzly')
        ex_rels = [('quantum-gateway', 'nova-cloud-controller'),
                   ('quantum-gateway', 'mysql'),
                   ('nova-cloud-controller', 'mysql')]
        self.assertEquals(ex_rels, list(deployment.get_relations()))


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

        config.urlopen = faux_urlopen
        config.load()
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
        config.urlopen = faux_urlopen
        self.assertRaises(ErrorExit, config.load)
