#coding: utf-8
import ConfigParser, os

class Config(object):

    def __init__(self, filename=""):
        if filename=="":
            filename = os.environ.get("WAE_CONF", "wae.conf")
            fs = [os.path.join(p, filename) for p in (".", "/usr/local/etc", "/usr/etc", "/etc")]
        else:
            if not os.path.exists(filename) or os.path.isdir(filename):
                raise Exception("cannot read config file '%s'" % filename)
            fs = [os.path.abspath(filename)]
        self._cp = ConfigParser.ConfigParser()
        self._conf = self._cp.read(fs)

    def _get_conf(self): 
        if len(self._conf)>0:
            return self._conf[0]
        else:
            return ""
    file = property(_get_conf)

    def get(self, section, key, default=""):
        try:
            return self._cp.get(section, key)
        except:
            return default

    def getint(self, section, key, default=0):
        try:
            return self._cp.getint(section, key)
        except:
            return default

    def getfloat(self, section, key, default=0.0):
        try:
            return self._cp.getfloat(section, key)
        except:
            return default

    def getbool(self, section, key, default=False):
        try:
            return self._cp.getboolean(section, key)
        except:
            return default

config = Config()

def set_config_file(f):
    global config
    config = Config(f)

