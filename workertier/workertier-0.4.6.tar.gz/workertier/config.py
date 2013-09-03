#coding:utf-8
import logging
import ConfigParser


CONFIG_CLASS_OPT = "class"


logger = logging.getLogger(__name__)


class ConfigLoader(object):
    def __init__(self, *config_paths):
        self.parser = ConfigParser.SafeConfigParser()
        self.read_paths = self.parser.read(config_paths)
        if not self.read_paths:
            logger.warning("No configuration file was found")

    def _normalize_opt(self, option):
        if option.isdigit():
            option = int(option)
        return option

    def _load_class(self, cls_path):
        module, cls = cls_path.rsplit(".", 1)

        try:
            _mod = __import__(module, fromlist=[cls])
        except ImportError:
            raise ImportError("Unable to import {0}".format(cls_path))
        else:
            return getattr(_mod, cls)

    def _get_object(self, section):
        cls_path = self.parser.get(section, CONFIG_CLASS_OPT)  # May raise an error
        cls = self._load_class(cls_path)
        kwargs = dict(((k, self._normalize_opt(v)) for k, v in self.parser.items(section) if k != CONFIG_CLASS_OPT))
        return cls(**kwargs)

    def cache(self):
        return self._get_object("cache")

    def dispatcher(self):
        return self._get_object("dispatcher")

    def safe_get(self, section, key, default=None):
        try:
            return self._normalize_opt(self.parser.get(section, key))
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return default
