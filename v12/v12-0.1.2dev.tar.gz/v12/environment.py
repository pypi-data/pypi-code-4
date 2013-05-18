import yaml
import os


class _Environment(object):
    def __init__(self):
        self.dev = False
        self.vars = {}

    @property
    def project_path(self):
        if not hasattr(self, "_project_path"):
            self._project_path = os.getcwd()
            while "app.yaml" not in os.listdir(self._project_path):
                if self._project_path == os.path.dirname(self._project_path):
                    print "could not find an app engine project root, exiting..."
                    exit()
                self._project_path = os.path.dirname(self._project_path)

        return self._project_path

    @property
    def v12_config(self):
        if not hasattr(self, "_v12_config"):
            config_path = os.path.join(self.project_path, "v12.yaml")
            if os.path.exists(config_path):
                with open(config_path) as config_file:
                    self._v12_config = yaml.load(config_file)
            else:
                self._v12_config = {}

        return self._v12_config

    @property
    def app_config(self):
        if not hasattr(self, "_app_config"):
            with open(os.path.join(self.project_path, "app.yaml")) as app_config_file:
                self._app_config = yaml.load(app_config_file)

        return self._app_config

env = _Environment()