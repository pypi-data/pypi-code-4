# -*- coding: utf-8 -*-
import os, ConfigParser
from os import path

CONFIG = {}
BLOCK_SIZE = 4 * 1024 * 1024
CHUNK_SIZE = 256 * 1024
RS_HOST    = "rs.qiniu.com"
RSF_HOST   = "rsf.qbox.me"
UP_HOST    = "up.qiniu.com"
VERSION    = '6.1.3'
USER_AGENT = "qiniu python-sdk v%s" % VERSION

def getcfg(sec, name, type=None, default=None):
    if sec not in CONFIG: return default
    if name not in CONFIG[sec]: return default
    if type: return type(CONFIG[sec][name])
    else: return CONFIG[sec][name]

def load_default_config(cfgfile):
    global CONFIG
    global BLOCK_SIZE
    global CHUNK_SIZE
    global RS_HOST
    global RSF_HOST
    global UP_HOST

    if not cfgfile: return
    cfgfile = path.expanduser(cfgfile)
    if not path.exists(cfgfile): return
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(cfgfile)

    for sec in cfg.sections():
        CONFIG[sec] = dict(cfg.items(sec))

    if CONFIG.get('main'):
        BLOCK_SIZE = CONFIG['main'].get('block_size') or BLOCK_SIZE
        CHUNK_SIZE = CONFIG['main'].get('chunk_size') or CHUNK_SIZE
    if CONFIG.get('hosts'):
        RS_HOST = CONFIG['hosts'].get('rs_host') or RS_HOST
        RSF_HOST = CONFIG['hosts'].get('rsf_host') or RSF_HOST
        UP_HOST = CONFIG['hosts'].get('up_host') or UP_HOST
    return CONFIG

def initcfgs(cfgfiles):
    for cfgfile in cfgfiles:
        if load_default_config(cfgfile):
            return True
    cfgfile = os.environ.get('QBOXCFG')
    if load_default_config(cfgfile):
        return True

class ErrorBase(StandardError): pass
class HttpError(ErrorBase): pass
class HttpRpcError(ErrorBase): pass
class BatchError(ErrorBase): pass
