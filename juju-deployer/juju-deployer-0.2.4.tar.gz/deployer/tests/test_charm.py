import os
import logging
import subprocess

from deployer.charm import Charm
from deployer.utils import ErrorExit

from .base import Base


class CharmTest(Base):

    def setUp(self):
        d = self.mkdir()
        self.series_path = os.path.join(d, "precise")
        os.mkdir(self.series_path)

        self.charm_data = {
            "charm": "couchdb",
            "build": None,
            "branch": "lp:charms/precise/couchdb",
            "rev": None,
            "charm_url": None,
        }
        self.output = self.capture_logging(
            "deployer.charm", level=logging.DEBUG)

    def test_vcs_charm(self):
        params = dict(self.charm_data)
        charm = Charm.from_service("scratch", self.series_path, params)

        charm.fetch()
        self.assertEqual(charm.metadata['name'],  'couchdb')

        charm.rev = 7
        charm.update()
        output = subprocess.check_output(
            ["bzr", "revno", "--tree"], cwd=charm.path)
        self.assertEqual(output.strip(), str(7))

        self.assertFalse(charm.is_modified())
        with open(os.path.join(charm.path, 'revision'), 'w') as fh:
            fh.write('0')
        self.assertTrue(charm.is_modified())

    def test_store_charm(self):
        pass

    def test_charm_error(self):
        params = dict(self.charm_data)
        params['branch'] = "lp:charms/precise/zebramoon"
        charm = Charm.from_service("scratch", self.series_path, params)
        self.assertRaises(ErrorExit, charm.fetch)
        self.assertIn('bzr: ERROR: Not a branch: ', self.output.getvalue())
