from django.conf import settings

import ConfigParser as configparser
from StringIO import StringIO


CMSPLUGIN_SECTION_TEMPLATES = getattr(settings, 'CMSPLUGIN_SECTION_TEMPLATES', ())

def get_options(options):
    cfg = configparser.RawConfigParser()
    try:
        cfg.readfp(StringIO(options))
    except configparser.MissingSectionHeaderError:
        cfg.readfp(StringIO('[default]\n' + options))
    result = {}
    try:
        for k, v in cfg.items('default'):
            result[k] = v
    except configparser.NoSectionError:
        pass
    return result
