import json
import logging
import os
import urllib
import shutil

from .vcs import Git, Bzr
from .utils import (
    _check_call,
    _get_juju_home,
    extract_zip,
    path_join,
    path_exists,
    temp_file,
    yaml_load)

STORE_URL = "https://store.juju.ubuntu.com"


class Charm(object):

    log = logging.getLogger('deployer.charm')

    def __init__(self, name, path, branch, rev, build, charm_url=""):
        self.name = name
        self._path = path
        self.branch = branch
        self.rev = rev
        self._charm_url = charm_url
        self._build = build
        self.vcs = self.get_vcs()

    def get_vcs(self):
        if not self.branch:
            return None
        if self.branch.startswith('git') or 'github.com' in self.branch or \
                os.path.exists(os.path.join(self.branch, '.git')):
            return Git(self.path, self.branch, self.log)
        elif self.branch.startswith("bzr") or self.branch.startswith('lp:') \
                or os.path.exists(os.path.join(self.branch, '.bzr')):
            return Bzr(self.path, self.branch, self.log)

    @classmethod
    def from_service(cls, name, series_path, d):
        branch, rev = None, None
        charm_branch = d.get('branch')
        if charm_branch is not None:
            branch, sep, rev = charm_branch.partition('@')

        charm_path, store_url, build = None, None, None
        name = d.get('charm', name)
        if name.startswith('cs:'):
            store_url = name
        else:
            charm_path = path_join(series_path, name)
            build = d.get('build', '')
        if not store_url:
            store_url = d.get('charm_url', None)

        if store_url and branch:
            cls.log.error(
                "Service: %s has both charm url: %s and branch: %s specified",
                name, store_url, branch)
        return cls(name, charm_path, branch, rev, build, store_url)

    def is_local(self):
        return not self._charm_url

    def exists(self):
        return self.is_local() and path_exists(self.path)

    def is_subordinate(self):
        return self.metadata.get('subordinate', False)

    @property
    def charm_url(self):
        if self._charm_url:
            return self._charm_url
        series = os.path.basename(os.path.dirname(self.path))
        charm_name = self.metadata['name']
        return "local:%s/%s" % (series, charm_name)

    def build(self):
        if not self._build:
            return
        self.log.debug("Building charm %s with %s", self.path, self._build)
        _check_call([self._build], self.log,
                    "Charm build failed %s @ %s", self._build, self.path,
                    cwd=self.path)

    def fetch(self):
        if self._charm_url:
            return self._fetch_store_charm()
        elif not self.branch:
            self.log.warning("Invalid charm specification %s", self.name)
            return
        self.log.debug(" Branching charm %s @ %s", self.branch, self.path)
        self.vcs.branch()
        self.build()

    @property
    def path(self):
        if not self.is_local() and not self._path:
            self._path = self._get_charm_store_cache()
        return self._path

    def _fetch_store_charm(self, update=False):
        cache_dir = self._get_charm_store_cache()
        self.log.debug("Cache dir %s", cache_dir)
        qualified_url = None

        if os.path.exists(cache_dir) and not update:
            return

        # If we have a qualified url, check cache and move on.
        parts = self.charm_url.rsplit('-', 1)
        if len(parts) > 1 and parts[-1].isdigit():
            qualified_url = self.charm_url

        if not qualified_url:
            info_url = "%s/charm-info?charms=%s" % (STORE_URL, self.charm_url)
            fh = urllib.urlopen(info_url)
            content = json.loads(fh.read())
            rev = content[self.charm_url]['revision']
            qualified_url = "%s-%d" % (self.charm_url, rev)

        self.log.debug("Retrieving store charm %s" % qualified_url)

        if update and os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

        with temp_file() as fh:
            ufh = urllib.urlopen("%s/charm/%s" % (
                STORE_URL, qualified_url[3:]))
            shutil.copyfileobj(ufh, fh)
            fh.flush()
            extract_zip(fh.name, self.path)

        self.config

    def _get_charm_store_cache(self):
        assert not self.is_local(), "Attempt to get store charm for local"
        # Cache
        jhome = _get_juju_home()
        cache_dir = os.path.join(jhome, ".deployer-store-cache")
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        return os.path.join(
            cache_dir,
            self.charm_url.replace(':', '_').replace("/", "_"))

    def update(self, build=False):
        if not self.branch:
            return
        assert self.exists()
        self.log.debug(" Updating charm %s from %s", self.path, self.branch)
        self.vcs.update(self.rev)
        if build:
            self.build()

    def is_modified(self):
        if not self.branch:
            return False
        return self.vcs.is_modified()

    @property
    def config(self):
        config_path = path_join(self.path, "config.yaml")
        if not path_exists(config_path):
            return {}

        with open(config_path) as fh:
            return yaml_load(fh.read()).get('options', {})

    @property
    def metadata(self):
        md_path = path_join(self.path, "metadata.yaml")
        if not path_exists(md_path):
            if not path_exists(self.path):
                raise RuntimeError("No charm metadata @ %s", md_path)
        with open(md_path) as fh:
            return yaml_load(fh.read())

    def get_provides(self):
        p = {'juju-info': [{'name': 'juju-info'}]}
        for key, value in self.metadata['provides'].items():
            value['name'] = key
            p.setdefault(value['interface'], []).append(value)
        return p

    def get_requires(self):
        r = {}
        for key, value in self.metadata['requires'].items():
            value['name'] = key
            r.setdefault(value['interface'], []).append(value)
        return r
