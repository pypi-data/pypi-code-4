__author__ = 'yarnaid'

import os
import subprocess as sp
import tempfile
import time

try:
    import tools.logger as lg
except:
    import glespy.tools.logger as lg


glesp_exec = '/usr/local/bin'
glesp = dict()
glesp['mappat'] = os.path.join(glesp_exec, 'mappat')
glesp['cl2map'] = os.path.join(glesp_exec, 'cl2map')
glesp['difmap'] = os.path.join(glesp_exec, 'difmap')
glesp['alm2dl'] = os.path.join(glesp_exec, 'alm2dl')
glesp['f2fig'] = os.path.join(glesp_exec, 'f2fig')
glesp['rsalm'] = os.path.join(glesp_exec, 'rsalm')
GIF_VIEWER = 'feh'

binaries = dict()
binaries.update(glesp)
binaries['viewer'] = os.path.join('/usr/bin', 'eog')

info = lg.logger.info
warn = lg.logger.warn
error = lg.logger.error
critical = lg.logger.critical
log = lg.logger.log
exception = lg.logger.exception
debug = lg.logger.debug

__all__ = ["run_cmd", "get_out_name", "glesp", "binaries",
           "info", "warn", "debug", "error", "critical", "log", "exception",
]


def run_cmd(args, debug_msg=None,
            shell=None,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            **kwargs):
    args = map(str, args)
    proc = sp.Popen(list(args),
                    stdout=stdout,
                    stderr=stderr,
                    shell=shell,
    )
    proc.wait()
    res = proc.communicate()
    # debug(args[0])
    if debug_msg:
        debug(debug_msg)
        # for stream in res:
        # l = stream.readlines()
        # if len(l) > 0:
        # debug(l)
    if len(res[0]):
        info(res[0])
    if len(res[1]):
        debug([res[1]])
    return res


def get_out_name(out_name=None, suffix='tmp', dir=None, **kwargs):
    # dir not tested!!!
    res = out_name
    if not res:
        tmp_file = tempfile.NamedTemporaryFile(dir=dir,
            suffix='_'.join([str(time.time()), suffix]),
            delete=kwargs.get('delete', True))
        res = tmp_file.name
    return res
