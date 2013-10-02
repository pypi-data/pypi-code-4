from copy import deepcopy
from contextlib import contextmanager

import errno
import logging
from logging.config import dictConfig as logConfig

import os
from os.path import (
    abspath,
    expanduser,
    isabs,
    isdir,
    join as path_join,
    exists as path_exists,
)

import stat
import subprocess
import time
import tempfile
import zipfile

try:
    from yaml import CSafeLoader, CSafeDumper
    SafeLoader, SafeDumper = CSafeLoader, CSafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

import yaml


class ErrorExit(Exception):

    def __init__(self, error=None):
        self.error = error

# Utility functions


def yaml_dump(value):
    return yaml.dump(value, default_flow_style=False)


def yaml_load(value):
    return yaml.load(value, Loader=SafeLoader)


DEFAULT_LOGGING = """
version: 1
formatters:
    standard:
        format: '%(asctime)s %(message)s'
        datefmt: "%Y-%m-%d %H:%M:%S"
    detailed:
        format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        datefmt: "%Y-%m-%d %H:%M:%S"
handlers:
    console:
        class: logging.StreamHandler
        formatter: standard
        level: DEBUG
        stream: ext://sys.stderr
loggers:
    deployer:
        level: INFO
        propogate: true
    deploy.cli:
        level: DEBUG
        propogate: true
    deploy.charm:
        level: DEBUG
        propogate: true
    deploy.env:
        level: DEBUG
        propogate: true
    deploy.deploy:
        level: DEBUG
        propogate: true
    deploy.importer:
        level: DEBUG
        propogate: true
    "":
        level: INFO
        handlers:
            - console
"""


def setup_logging(verbose=False, debug=False, stream=None):
    config = yaml_load(DEFAULT_LOGGING)
    log_options = {}
    if verbose:
        log_options.update({"loggers": {
            "deployer": {"level": "DEBUG", "propogate": True}}})
        #log_options.update({"loggers": {""
    if debug:
        log_options.update(
            {"handlers": {"console": {"formatter": "detailed"}}})
    config = dict_merge(config, log_options)
    logConfig(config)

    # Allow tests to reuse this func to mass configure log streams.
    if stream:
        root = logging.getLogger()
        previous = root.handlers[0]
        root.handlers[0] = current = logging.StreamHandler(stream)
        current.setFormatter(previous.formatter)
        return stream


@contextmanager
def temp_file():
    t = tempfile.NamedTemporaryFile()
    try:
        yield t
    finally:
        t.close()


def extract_zip(zip_path, dir_path):
    zf = zipfile.ZipFile(zip_path, "r")
    for info in zf.infolist():
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            source = zf.read(info.filename)
            target = os.path.join(dir_path, info.filename)
            if os.path.exists(target):
                os.remove(target)
            os.symlink(source, target)
            continue
        extract_path = zf.extract(info, dir_path)
        os.chmod(extract_path, mode)


def _parse_constraints(value):
    constraints = {}
    pairs = value.strip().split()
    for p in pairs:
        k, v = p.split('=')
        try:
            v = int(v)
        except ValueError:
            try:
                v = float(v)
            except:
                pass
        constraints[k] = v
    return constraints


def _get_juju_home():
    jhome = os.environ.get("JUJU_HOME")
    if jhome is None:
        jhome = path_join(os.environ.get('HOME'), '.juju')
    return jhome


def _check_call(params, log, *args, **kw):
    max_retry = kw.get('max_retry', None)
    cur = kw.get('cur_try', 1)
    try:
        cwd = abspath(".")
        if 'cwd' in kw:
            cwd = kw['cwd']
        stderr = subprocess.STDOUT
        if 'stderr' in kw:
            stderr = kw['stderr']
        output = subprocess.check_output(
            params, cwd=cwd, stderr=stderr, env=os.environ)
    except subprocess.CalledProcessError, e:
        if 'ignoreerr' in kw:
            return
        #print "subprocess error"
        #print " ".join(params), "\ncwd: %s\n" % cwd, "\n ".join(
        # ["%s=%s" % (k, os.environ[k]) for k in os.environ
        #     if k.startswith("JUJU")])
        #print e.output
        log.error(*args)
        log.error("Command (%s) Output:\n\n %s", " ".join(params), e.output)
        if not max_retry or cur > max_retry:
            raise ErrorExit(e)
        kw['cur_try'] = cur + 1
        log.error("Retrying (%s of %s)" % (cur, max_retry))
        time.sleep(1)
        output = _check_call(params, log, args, **kw)
    return output


# Utils from deployer 1
def relations_combine(onto, source):
    target = deepcopy(onto)
    # Support list of relations targets
    if isinstance(onto, list) and isinstance(source, list):
        target.extend(source)
        return target
    for (key, value) in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                target[key] = relations_combine(target[key], value)
            elif isinstance(target[key], list) and isinstance(value, list):
                target[key] = list(set(target[key] + value))
        else:
            target[key] = value
    return target


def dict_merge(onto, source):
    target = deepcopy(onto)
    for (key, value) in source.items():
        if key == 'relations' and key in target:
            target[key] = relations_combine(target[key], value)
        elif (key in target and isinstance(target[key], dict) and
                isinstance(value, dict)):
            target[key] = dict_merge(target[key], value)
        else:
            target[key] = value
    return target


def resolve_include(fname, include_dirs):
    if isabs(fname):
        return fname
    for path in include_dirs:
        full_path = path_join(path, fname)
        if path_exists(full_path):
            return full_path

    return None


def mkdir(path):
    """Create a leaf directory and all intermediate ones.

    Also expand ~ and ~user constructions.
    If path exists and it's a directory, return without errors.
    """
    path = expanduser(path)
    try:
        os.makedirs(path)
    except OSError as err:
        # Re-raise the error if the target path exists but it is not a dir.
        if (err.errno != errno.EEXIST) or (not isdir(path)):
            raise
