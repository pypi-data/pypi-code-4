import base64
import StringIO
import os


from deployer.config import ConfigStack
from deployer.deployment import Deployment
from deployer.utils import setup_logging

from .base import Base


class DeploymentTest(Base):

    def setUp(self):
        self.output = setup_logging(
            debug=True, verbose=True, stream=StringIO.StringIO())

    def test_deployer(self):
        d = ConfigStack(
            [os.path.join(
                self.test_data_dir, "blog.yaml")]).get('wordpress-prod')
        services = d.get_services()
        self.assertTrue([s for s in services if s.name == "newrelic"])

        # Ensure inheritance order reflects reality, instead of merge value.
        self.assertEqual(
            d.data['inherits'],
            ['wordpress-stage', 'wordpress-base', 'metrics-base'])

        # Fetch charms to verify late binding config values & validation.
        t = self.mkdir()
        os.mkdir(os.path.join(t, "precise"))
        d.repo_path = t
        d.fetch_charms()

        # Load up overrides and resolves
        d.load_overrides(["key=abc"])
        d.resolve_config()

        # Verify include-base64
        self.assertEqual(d.get_service('newrelic').config, {'key': 'abc'})
        self.assertEqual(
            base64.b64decode(d.get_service('blog').config['wp-content']),
            "HelloWorld")

        # TODO verify include-file

        # Verify relations
        self.assertEqual(
            list(d.get_relations()),
            [('blog', 'db'), ('blog', 'cache'), ('blog', 'haproxy')])

    def test_multiple_relations_no_weight(self):
        data = {"relations": {"wordpress": {"consumes": ["mysql"]},
                              "nginx": {"consumes": ["wordpress"]}}}
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('nginx', 'wordpress'), ('wordpress', 'mysql')],
            list(d.get_relations()))

    def test_multiple_relations_weighted(self):
        data = {
            "relations": {
                "keystone": {
                    "weight": 100,
                    "consumes": ["mysql"]
                },
                "nova-compute": {
                    "weight": 50,
                    "consumes": ["mysql"]
                },
                "glance": {
                    "weight": 70,
                    "consumes": ["mysql"]
                },
            }
        }
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('keystone', 'mysql'), ('glance', 'mysql'),
             ('nova-compute', 'mysql')], list(d.get_relations()))
