from os.path import dirname, abspath
import logging
import tempfile
import shutil
import urllib
import urlparse


from .deployment import Deployment
from .utils import ErrorExit, yaml_load, path_exists, dict_merge


class ConfigStack(object):

    log = logging.getLogger("deployer.config")

    def __init__(self, config_files):
        self.config_files = config_files
        self.data = {}
        self.include_dirs = []
        self.load()

    def keys(self):
        return sorted(self.data)

    def get(self, key):
        if not key in self.data:
            self.log.warning("Deployment %r not found. Available %s",
                             key, ", ".join(self.keys()))
            raise ErrorExit()
        deploy_data = self.data[key]
        deploy_data = self._resolve_inherited(deploy_data)
        return Deployment(key, deploy_data, self.include_dirs)

    def load(self, urlopen=urllib.urlopen):
        data = {}
        include_dirs = []
        for fp in self.config_files:
            if not path_exists(fp):
                # If the config file path is a URL, fetch it and use it.
                if urlparse.urlparse(fp).scheme:
                    response = urlopen(fp)
                    if response.getcode() == 200:
                        temp = tempfile.NamedTemporaryFile(delete=True)
                        shutil.copyfileobj(response, temp)
                        temp.flush()
                        fp = temp.name
                    else:
                        self.log.warning("Could not retrieve %s", fp)
                        raise ErrorExit()
                else:
                    self.log.warning("Config file not found %s", fp)
                    raise ErrorExit()
            else:
                include_dirs.append(dirname(abspath(fp)))
            with open(fp) as fh:
                try:
                    d = yaml_load(fh.read())
                    data = dict_merge(data, d)
                except Exception, e:
                    self.log.warning(
                        "Couldn't load config file @ %r, error: %s:%s",
                        fp, type(e), e)
                    raise
        self.data = data
        self.include_dirs = include_dirs

    def _inherits(self, d):
        parents = d.get('inherits', ())
        if isinstance(parents, basestring):
            parents = [parents]
        return parents

    def _resolve_inherited(self, deploy_data):
        if not 'inherits' in deploy_data:
            return deploy_data
        inherits = parents = self._inherits(deploy_data)
        for parent_name in parents:
            parent = self.get(parent_name)
            inherits.extend(self._inherits(parent.data))
            deploy_data = dict_merge(deploy_data, parent.data)
        deploy_data['inherits'] = inherits
        return deploy_data
