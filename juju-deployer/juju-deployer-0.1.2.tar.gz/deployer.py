#!/usr/bin/env python
"""
Juju Deployer

Deployment automation for juju.

"""
import argparse
from base64 import b64encode
from bzrlib.workingtree import WorkingTree
from copy import deepcopy
from contextlib import contextmanager

import errno
import json
import logging
from logging.config import dictConfig as logConfig
import os

from os.path import abspath, dirname, isabs
from os.path import join as path_join
from os.path import exists as path_exists

import pprint
import shutil
import stat
import socket
import subprocess
import sys
import tempfile
import time
import urllib
import urlparse
import zipfile

try:
    from yaml import CSafeLoader, CSafeDumper
    SafeLoader, SafeDumper = CSafeLoader, CSafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

import yaml


from jujuclient import (
    Environment as EnvironmentClient, UnitErrors, EnvError)


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

STORE_CACHE_DIR = "deployer-cache"

STORE_URL = "https://store.juju.ubuntu.com"


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


def select_runtime(env_name):
    # pyjuju does juju --version
    result = _check_call(["juju", "version"], None, ignoreerr=True)
    if result is None:
        return PyEnvironment(env_name)
    return GoEnvironment(env_name)


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
        raise ErrorExit(e)
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


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help=('File containing deployment(s) json config. This '
              'option can be repeated, with later files overriding '
              'values in earlier ones.'),
        dest='configs', action='append')
    parser.add_argument(
        '-d', '--debug', help='Enable debugging to stdout',
        dest="debug",
        action="store_true", default=False)
    parser.add_argument(
        '-L', '--local-mods',
        help='Disallow deployment of locally-modified charms',
        dest="no_local_mods", default=True, action='store_false')
    parser.add_argument(
        '-u', '--update-charms',
        help='Update existing charm branches',
        dest="update_charms", default=False, action="store_true")
    parser.add_argument(
        '-l', '--ls', help='List available deployments',
        dest="list_deploys", action="store_true", default=False)
    parser.add_argument(
        '-D', '--destroy-services',
        help='Destroy all services (do not terminate machines)',
        dest="destroy_services", action="store_true",
        default=False)
    parser.add_argument(
        '-T', '--terminate-machines',
        help=('Terminate all machines but the bootstrap node.  '
              'Destroy any services that exist on each'),
        dest="terminate_machines", action="store_true",
        default=False)
    parser.add_argument(
        '-t', '--timeout',
        help='Timeout (sec) for entire deployment (45min default)',
        dest='timeout', action='store', type=int, default=2700)
    parser.add_argument(
        "-f", '--find-service', action="store", type=str,
        help='Find hostname from first unit of a specific service.',
        dest="find_service")
    parser.add_argument(
        "-b", '--branch-only', action="store_true",
        help='Update vcs branches and exit.',
        dest="branch_only")
    parser.add_argument(
        '-s', '--deploy-delay', action='store', type=float,
        help=("Time in seconds to sleep between 'deploy' commands, "
              "to allow machine provider to process requests. On "
              "terminate machines this also signals waiting for "
              "machine removal."),
        dest="deploy_delay", default=0)
    parser.add_argument(
        '-e', '--environment', action='store', dest='juju_env',
        help='Deploy to a specific Juju environment.',
        default=os.getenv('JUJU_ENV'))
    parser.add_argument(
        '-o', '--override', action='append', type=str,
        help=('Override *all* config options of the same name '
              'across all services.  Input as key=value.'),
        dest='overrides', default=None)
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        dest="verbose", help='Verbose output')
    parser.add_argument(
        '-W', '--watch', help='Watch environment changes on console',
        dest="watch", action="store_true", default=False)
    parser.add_argument(
        '-r', "--retry", default=0, type=int, dest="retry_count",
        help=("Resolve unit errors via retry."
              " Either standalone or in a deployment"))
    parser.add_argument(
        "--diff", action="store_true", default=False,
        help=("Resolve unit errors via retry."
              " Either standalone or in a deployment"))
    parser.add_argument(
        '-w', '--relation-wait', action='store', dest='rel_wait',
        default=60, type=int,
        help=('Number of seconds to wait before checking for '
              'relation errors after all relations have been added '
              'and subordinates started. (default: 60)'))
    parser.add_argument("deployment", nargs="?")
    return parser


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


class Endpoint(object):

    def __init__(self, ep):
        self.ep = ep
        self.name = None
        if ":" in self.ep:
            self.service, self.name = self.ep.split(":")
        else:
            self.service = ep


class EndpointPair(object):
    # Really simple endpoint service matching that does not work for multiple
    # relations between two services (used by diff at the moment)

    def __init__(self, ep_x, ep_y=None):
        self.ep_x = Endpoint(ep_x)
        self.ep_y = ep_y and Endpoint(ep_y)

    def __eq__(self, ep_pair):
        if not isinstance(ep_pair, EndpointPair):
            return False
        return (ep_pair.ep_x.service in self
                and
                ep_pair.ep_y.service in self)

    def __contains__(self, svc_name):
        return (svc_name == self.ep_x.service
                or
                svc_name == self.ep_y.service)

    def __hash__(self):
        return hash(tuple(sorted(
            (self.ep_x.service, self.ep_y.service))))

    def __repr__(self):
        return "%s <-> %s" % (
            self.ep_x.ep,
            self.ep_y.ep)

    @staticmethod
    def to_yaml(dumper, data):
        return dumper.represent_list([[data.ep_x.ep, data.ep_y.ep]])


yaml.add_representer(EndpointPair, EndpointPair.to_yaml)


class Service(object):

    def __init__(self, name, svc_data):
        self.svc_data = svc_data
        self.name = name

    @property
    def config(self):
        return self.svc_data.get('options', None)

    @property
    def constraints(self):
        return self.svc_data.get('constraints', None)

    @property
    def num_units(self):
        return int(self.svc_data.get('num_units', 1))

    @property
    def force_machine(self):
        return self.svc_data.get('force-machine')

    @property
    def expose(self):
        return self.svc_data.get('expose', False)


class Vcs(object):

    err_update = (
        "Could not update branch %(path)s from %(branch_url)s\n\n %(output)s")
    err_branch = "Could not branch %(branch_url)s to %(path)s\n\n %(output)s"
    err_is_mod = "Couldn't determine if %(path)s was modified\n\n %(output)s"
    err_pull = (
        "Could not pull branch @ %(branch_url)s to %(path)s\n\n %(output)s")
    err_cur_rev = (
        "Could not determine current revision %(path)s\n\n %(output)s")

    def __init__(self, path, origin, log):
        self.path = path
        self.log = log
        self.origin = origin

    def _call(self, args, error_msg, cwd=None, stderr=()):
        try:
            stderr = stderr is None and stderr or subprocess.STDOUT
            output = subprocess.check_output(
                args, cwd=cwd or self.path, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            #print "vcs err", " ".join(args), "[dir: %s]" % cwd
            self.log.error(error_msg % self.get_err_msg_ctx(e))
            raise ErrorExit()
        return output.strip()

    def get_err_msg_ctx(self, e):
        return {
            'path': self.path,
            'branch_url': self.origin,
            'exit_code': e.returncode,
            'output': e.output,
            'vcs': self.__class__.__name__.lower()}

    def get_cur_rev(self):
        raise NotImplementedError()

    def update(self, rev=None):
        raise NotImplementedError()

    def branch(self):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    def is_modified(self):
        raise NotImplementedError()

    # upstream missing revisions?


class Bzr(Vcs):

    def get_cur_rev(self):
        params = ["bzr", "revno", "--tree"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["bzr", "up"]
        if rev:
            params.extend(["-r", str(rev)])
        self._call(params, self.err_update)

    def pull(self):
        params = ["bzr", "pull", "--remember", self.origin]
        self._call(params, self.err_pull)

    def branch(self):
        params = ["bzr", "branch", self.origin, self.path]
        cwd = os.path.dirname(os.path.dirname(self.path))
        if not cwd:
            cwd = "."
        self._call(params, self.err_branch, cwd)

    def is_modified(self):
        # To replace with bzr cli, we need to be able to detect
        # changes to a wc @ a rev or @ trunk.
        tree = WorkingTree.open(self.path)
        return tree.has_changes()


class Git(Vcs):

    def get_cur_rev(self):
        params = ["git", "rev-parse", "HEAD"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["git", "reset", "--merge"]
        if rev:
            params.append(rev)
        self._call(params, self.err_update)

    def pull(self):
        params = ["git", "pull", "master"]
        self._call(params, self.err_pull)

    def branch(self):
        params = ["git", "clone", self.branch]
        self._call(params, self.err_branch, os.path.dirname(self.path))

    def is_modified(self):
        params = ["git", "stat", "-s"]
        return bool(self._call(params, self.err_is_mod).strip())

    def get_origin(self):
        params = ["git", "config", "--get", "remote.origin.url"]
        return self._call(params, "")


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
        if self.branch.startswith('git') or 'github.com' in self.branch:
            return Git(self.path, self.branch, self.log)
        elif self.branch.startswith("bzr") or self.branch.startswith('lp:'):
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
        return "local:%s/%s" % (series, self.name)

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


class Deployment(object):

    log = logging.getLogger("deployer.deploy")

    def __init__(self, name, data, include_dirs, repo_path=""):
        self.name = name
        self.data = data
        self.include_dirs = include_dirs
        self.repo_path = repo_path

    @property
    def series(self):
        # Series could use a little help, charm series should be inferred
        # directly from a store url
        return self.data.get('series', 'precise')

    @property
    def series_path(self):
        return path_join(self.repo_path, self.series)

    def pretty_print(self):
        pprint.pprint(self.data)

    def get_service(self, name):
        if not name in self.data['services']:
            return
        return Service(name, self.data['services'][name])

    def get_services(self):
        for name, svc_data in self.data.get('services', {}).items():
            yield Service(name, svc_data)

    def get_relations(self):
        if 'relations' not in self.data:
            return

        # Strip duplicate rels
        seen = set()

        def check(a, b):
            k = tuple(sorted([a, b]))
            if k in seen:
                #self.log.warning(" Skipping duplicate relation %r" % (k,))
                return
            seen.add(k)
            return True

        # Support an ordered list of [endpoints]
        if isinstance(self.data['relations'], list):
            for end_a, end_b in self.data['relations']:
                # Allow shorthand of [end_a, [end_b, end_c]]
                if isinstance(end_b, list):
                    for eb in end_b:
                        if check(end_a, eb):
                            yield (end_a, eb)
                else:
                    if check(end_a, end_b):
                        yield (end_a, end_b)
            return

        # Legacy format (dictionary of dictionaries with weights)
        rels = {}
        for k, v in self.data['relations'].items():
            expanded = []
            for c in v['consumes']:
                expanded.append((k, c))
            by_weight = rels.setdefault(v.get('weight', 0), [])
            by_weight.extend(expanded)
        for k in sorted(rels):
            for r in rels[k]:
                if check(*r):
                    yield r
        #self.log.debug(
        #    "Found relations %s\n  %s" % (" ".join(map(str, seen))))

    def get_charms(self):
        for k, v in self.data.get('services', {}).items():
            yield Charm.from_service(k, self.series_path, v)

    def get_charm_for(self, svc_name):
        svc_data = self.data['services'][svc_name]
        return Charm.from_service(svc_name, self.series_path, svc_data)

    def fetch_charms(self, update=False, no_local_mods=False):
        if not os.path.exists(self.series_path):
            os.mkdir(self.series_path)
        for charm in self.get_charms():
            if charm.is_local():
                if charm.exists():
                    if no_local_mods:
                        if charm.is_modified():
                            self.log.warning(
                                "Charm %r has local modifications",
                                charm.path)
                            raise ErrorExit()
                    if update:
                        charm.update(build=True)
                    return
            charm.fetch()

    def resolve(self, cli_overides=()):
        # Once we have charms definitions available, we can do verification
        # of config options.
        self.load_overrides(cli_overides)
        self.resolve_config()
        self.validate_relations()

    def load_overrides(self, cli_overrides=()):
        """Load overrides."""
        overrides = {}
        overrides.update(self.data.get('overrides', {}))

        for o in cli_overrides:
            key, value = o.split('=', 1)
            overrides[key] = value

        for k, v in overrides.iteritems():
            found = False
            for svc_name, svc_data in self.data['services'].items():
                charm = self.get_charm_for(svc_name)
                if k in charm.config:
                    svc_data['options'][k] = v
                    found = True
            if not found:
                self.log.warning(
                    "Override %s does not match any charms", k)

    def resolve_config(self):
        """Load any lazy config values (includes), and verify config options.
        """
        self.log.debug("Resolving configuration")
        # XXX TODO, rename resolve, validate relations
        # against defined services
        for svc_name, svc_data in self.data.get('services', {}).items():
            if not 'options' in svc_data:
                continue
            charm = self.get_charm_for(svc_name)
            config = charm.config
            options = {}

            for k, v in svc_data['options'].items():
                if not k in config:
                    self.log.error(
                        "Invalid config charm %s %s=%s", charm.name, k, v)
                    raise ErrorExit()
                iv = self._resolve_include(svc_name, k, v)
                if iv is not None:
                    v = iv
                options[k] = v
            svc_data['options'] = options

    def _resolve_include(self, svc_name, k, v):
        for include_type in ["file", "base64"]:
            if (not isinstance(v, basestring)
                or not v.startswith(
                    "include-%s://" % include_type)):
                continue
            include, fname = v.split("://", 1)
            ip = resolve_include(fname, self.include_dirs)
            if ip is None:
                self.log.warning(
                    "Invalid config %s.%s include not found %s",
                    svc_name, k, v)
                continue
            with open(ip) as fh:
                v = fh.read()
                if include_type == "base64":
                    v = b64encode(v)
                return v

    def validate_relations(self):
        # Could extend to do interface matching against charms.
        services = dict([(s.name, s) for s in self.get_services()])
        for e_a, e_b in self.get_relations():
            for ep in [Endpoint(e_a), Endpoint(e_b)]:
                if not ep.service in services:
                    self.log.error(
                        ("Invalid relation in config,"
                         " service %s not found, rel %s"),
                        ep.service, "%s <-> %s" % (e_a, e_b))
                    raise ErrorExit()

    def save(self, path):
        with open(path, "w") as fh:
            fh.write(yaml_dump(self.data))

    @staticmethod
    def to_yaml(dumper, deployment):
        return dumper.represent_dict(deployment.data)

yaml.add_representer(Deployment, Deployment.to_yaml)


class BaseEnvironment(object):

    log = logging.getLogger("deployer.env")

    @property
    def env_config_path(self):
        jhome = _get_juju_home()
        env_config_path = path_join(jhome, 'environments.yaml')
        return env_config_path

    def _named_env(self, params):
        if self.name:
            params.extend(["-e", self.name])
        return params

    def _get_env_config(self):
        with open(self.env_config_path) as fh:
            config = yaml_load(fh.read())
            if self.name:
                if self.name not in config['environments']:
                    self.log.error("Environment %r not found", self.name)
                    raise ErrorExit()
                return config['environments'][self.name]
            else:
                env_name = config.get('default')
                if env_name is None:
                    if len(config['environments'].keys()) == 1:
                        env_name = config['environments'].keys().pop()
                    else:
                        self.log.error("Ambigious operation environment")
                        raise ErrorExit()
                return config['environments'][env_name]

    def _write_config(self, svc_name, config, fh):
        fh.write(yaml_dump({svc_name: config}))
        fh.flush()

#    def _write_config(self, svc_name, config, fh):
#        fh.write(yaml_dump(config))
#        fh.flush()

    def _get_units_in_error(self, status=None):
        units = []
        if status is None:
            status = self.status()
        for s in status.get('services', {}).keys():
            for uid, u in status['services'][s].get('units', {}).items():
                if 'error' in u['agent-state']:
                    units.append(uid)
                for uid, u in u.get('subordinates', {}).items():
                    if 'error' in u['agent-state']:
                        units.append(uid)
        return units

    def deploy(self, name, charm_url,
               repo=None, config=None,
               constraints=None, num_units=1, force_machine=None):
        params = self._named_env(["juju", "deploy"])
        with temp_file() as fh:
            if config:
                fh.write(yaml_dump({name: config}))
                fh.flush()
                params.extend(["--config", fh.name])
            if constraints:
                params.extend(['--constraints', constraints])
            if num_units != 1:
                params.extend(["--num-units", str(num_units)])
            if charm_url.startswith('local'):
                if repo == "":
                    repo = "."
                params.extend(["--repository=%s" % repo])
            if force_machine is not None:
                params.extend["--force-machine=%d" % force_machine]

            params.extend([charm_url, name])
            _check_call(params, self.log, "Error deploying service %r", name)

    def terminate_machine(self, mid, wait=False):
        """Terminate a machine.

        The machine can't have any running units, after removing the units or
        destroying the service, use wait_for_units to know when its safe to
        delete the machine (ie units have finished executing stop hooks and are
        removed)
        """
        if int(mid) == 0:
            raise RuntimeError("Can't terminate machine 0")
        params = self._named_env(["juju", "terminate-machine"])
        params.append(mid)
        try:
            _check_call(params, self.log, "Error terminating machine %r" % mid)
        except ErrorExit, e:
            if ("machine %s does not exist" % mid) in e.error.output:
                return
            raise

    def get_service_address(self, svc_name):
        status = self.get_cli_status()
        if svc_name not in status['services']:
            self.log.warning("Service %s does not exist", svc_name)
            return None
        units = status['services'][svc_name].get('units', {})
        unit_keys = list(sorted(units.keys()))
        if unit_keys:
            return units[unit_keys[0]].get('public-address', '')
        self.log.warning("Service %s has no units")

    def get_cli_status(self):
        params = self._named_env(["juju", "status"])
        with open('/dev/null', 'w') as fh:
            output = _check_call(
                params, self.log, "Error getting status, is it bootstrapped?",
                stderr=fh)
        status = yaml_load(output)
        return status


class PyEnvironment(BaseEnvironment):

    def __init__(self, name):
        self.name = name

    def add_units(self, service_name, num_units):
        params = self._named_env(["juju", "add-unit"])
        if num_units > 1:
            params.extend(["-n", str(num_units)])
        params.append(service_name)
        _check_call(
            params, self.log, "Error adding units to %s", service_name)

    def add_relation(self, endpoint_a, endpoint_b):
        params = self._named_env(["juju", "add-relation"])
        params.extend([endpoint_a, endpoint_b])
        _check_call(
            params, self.log, "Error adding relation to %s %s",
            endpoint_a, endpoint_b)

    def close(self):
        """ NoOp """

    def connect(self):
        """ NoOp """

    def _destroy_service(self, service_name):
        params = self._named_env(["juju", "destroy-service"])
        params.append(service_name)
        _check_call(
            params, self.log, "Error destroying service %s" % service_name)

    def get_config(self, svc_name):
        params = self._named_env(["juju", "get"])
        params.append(svc_name)
        return _check_call(
            params, self.log, "Error retrieving config for %r", svc_name)

    def get_constraints(self, svc_name):
        params = self._named_env(["juju", "get-constraints"])
        params.append(svc_name)
        return _check_call(
            params, self.log, "Error retrieving constraints for %r", svc_name)

    def reset(self,
              terminate_machines=False,
              terminate_delay=0,
              timeout=360,
              watch=False):
        status = self.status()
        for s in status.get('services'):
            self.log.debug(" Destroying service %s", s)
            self._destroy_service(s)
        if not terminate_machines:
            return True
        for m in status.get('machines'):
            if int(m) == 0:
                continue
            self.log.debug(" Terminating machine %s", m)
            self.terminate_machine(str(m))
            if terminate_delay:
                self.log.debug("  Waiting for terminate delay")
                time.sleep(terminate_delay)

    def resolve_errors(self, retry_count=0, timeout=600, watch=False, delay=5):
        pass

    def status(self):
        return self.get_cli_status()

    def wait_for_units(
            self, timeout, goal_state="started", watch=False, no_exit=False):

        max_time = time.time() + timeout
        while max_time > time.time():
            status = self.status()
            pending = []
            error_units = self._get_units_in_error(status)
            errors = []
            for s in status.get("services", {}).values():
                for uid, u in s.get("units", {}).items():
                    state = u.get("agent-state") or "pending"
                    if uid in error_units:
                        errors.append({"name": uid,
                                       "machine": u["machine"],
                                       "agent-state": state})
                    elif state != goal_state:
                        pending.append(u)
                    for rid in u.get("relation-errors", {}).keys():
                        errors.append({"name": uid,
                                       "machine": u["machine"],
                                       "agent-state":
                                       "relation-error: %s" % rid})
                    for sid, sub in u.get("subordinates", {}).items():
                        state = sub.get("agent-state") or "pending"
                        if sid in error_units:
                            errors.append({"name": sid,
                                           "machine": u["machine"],
                                           "agent-state": state})
                        elif state != goal_state:
                            pending.append(sid)
            if not pending and not errors:
                break
            if errors:
                if no_exit:
                    raise UnitErrors(errors)
                else:
                    error_units = [
                        "unit: %s: machine: %s agent-state: %s" % (
                            u["name"], u["machine"], u["agent-state"]
                            )
                        for u in errors]
                    self.log.error(
                        "The following units had errors:\n  %s" % (
                            "   \n".join(error_units)))
                    raise ErrorExit()


class GoEnvironment(BaseEnvironment):

    def __init__(self, name, endpoint=None):
        self.name = name
        self.api_endpoint = endpoint
        self.client = None

    def _get_token(self):
        config = self._get_env_config()
        return config['admin-secret']

    def add_units(self, service_name, num_units):
        return self.client.add_units(service_name, num_units)

    def add_relation(self, endpoint_a, endpoint_b):
        return self.client.add_relation(endpoint_a, endpoint_b)

    def close(self):
        if self.client:
            self.client.close()

    def connect(self):
        if not self.api_endpoint:
            # Should really have a cheaper/faster way of getting the endpoint
            # ala juju status 0 for a get_endpoint method.
            self.get_cli_status()
        while True:
            try:
                self.client = EnvironmentClient(self.api_endpoint)
            except socket.error, e:
                if e.errno != errno.ETIMEDOUT:
                    raise
                continue
            else:
                break
        self.client.login(self._get_token())
        self.log.debug("Connected to environment")

    def get_config(self, svc_name):
        return self.client.get_config(svc_name)

    def get_constraints(self, svc_name):
        return self.client.get_constraints(svc_name)

    def get_cli_status(self):
        status = super(GoEnvironment, self).get_cli_status()
        # Opportunistic, see connect method comment.
        if not self.api_endpoint:
            self.api_endpoint = "wss://%s:17070/" % (
                status["machines"]["0"]["dns-name"])
        return status

    def reset(self,
              terminate_machines=False,
              terminate_wait=False,
              timeout=360, watch=False):
        """Destroy/reset the environment."""
        status = self.status()
        destroyed = False
        for s in status.get('services', {}).keys():
            self.log.debug(" Destroying service %s", s)
            self.client.destroy_service(s)
            destroyed = True

        if destroyed:
            # Mark any errors as resolved so destruction can proceed.
            self.resolve_errors()

            # Wait for units
            self.wait_for_units(timeout, "removed", watch=watch)

        # The only value to not terminating is keeping the data on the
        # machines around.
        if not terminate_machines:
            self.log.info(
                " warning: juju-core machines are not reusable for units")
            return
        self._terminate_machines(status, watch, terminate_wait)

    def _terminate_machines(self, status, watch, terminate_wait):
        """Terminate all machines, optionally wait for termination.
        """
        # Terminate machines
        self.log.debug(" Terminating machines")

        # Don't bother if there are no service unit machines
        if len(status['machines']) == 1:
            return

        for mid in status['machines'].keys():
            if mid == "0":
                continue
            self.log.debug("  Terminating machine %s", mid)
            self.terminate_machine(mid)

        if terminate_wait:
            self.log.info("  Waiting for machine termination")
            callback = watch and self._delta_event_log or None
            self.client.wait_for_no_machines(None, callback)

    def _check_timeout(self, etime):
        w_timeout = etime - time.time()
        if w_timeout < 0:
            self.log.error("Timeout reached while resolving errors")
            raise ErrorExit()
        return w_timeout

    def resolve_errors(self, retry_count=0, timeout=600, watch=False, delay=5):
        """Resolve any unit errors in the environment.

        If retry_count is given then the hook execution is reattempted. The
        system will do up to retry_count passes through the system resolving
        errors.

        If retry count is not given, the error is marked resolved permanently.
        """
        etime = time.time() + timeout
        count = 0
        while True:
            error_units = self._get_units_in_error()
            for e_uid in error_units:
                try:
                    self.client.resolved(e_uid, retry=bool(retry_count))
                    self.log.debug("  Resolving error on %s", e_uid)
                except EnvError, e:
                    if 'already resolved' in e:
                        continue

            if not error_units and count:
                if not count:
                    self.log.debug("  No unit errors found.")
                else:
                    self.log.debug("  No more unit errors found.")
                return

            w_timeout = self._check_timeout(etime)
            if retry_count:
                time.sleep(delay)

            count += 1
            try:
                self.wait_for_units(
                    timeout=int(w_timeout), watch=True, no_exit=True)
            except UnitErrors, e:
                if retry_count == count:
                    self.log.info(
                        " Retry count %d exhausted, but units in error (%s)",
                        retry_count, " ".join(u['Name'] for u in e.errors))
                    return
            else:
                return

    def status(self):
        return self.client.get_stat()

    def wait_for_units(
            self, timeout, goal_state="started", watch=False, no_exit=False):
        """Wait for units to reach a given condition.
        """
        callback = watch and self._delta_event_log or None
        try:
            self.client.wait_for_units(timeout, goal_state, callback=callback)
        except UnitErrors, e:
            error_units = [
                "unit: %s: machine: %s agent-state: %s details: %s" % (
                    u['Name'], u['MachineId'], u['Status'], u['StatusInfo']
                )
                for u in e.errors]
            if no_exit:
                raise
            self.log.error("The following units had errors:\n   %s" % (
                "   \n".join(error_units)))
            raise ErrorExit()

    def _delta_event_log(self, et, ct, d):
        # event type, change type, data
        name = d.get('Name', d.get('Id', 'unknown'))
        state = d.get('Status', d.get('Life', 'unknown'))
        if et == "relation":
            name = self._format_endpoints(d['Endpoints'])
            state = "created"
            if ct == "remove":
                state = "removed"
        self.log.debug(
            " Delta %s: %s %s:%s", et, name, ct, state)

    def _format_endpoints(self, eps):
        if len(eps) == 1:
            ep = eps.pop()
            return "[%s:%s:%s]" % (
                ep['ServiceName'],
                ep['Relation']['Name'],
                ep['Relation']['Role'])

        return "[%s:%s <-> %s:%s]" % (
            eps[0]['ServiceName'],
            eps[0]['Relation']['Name'],
            eps[1]['ServiceName'],
            eps[1]['Relation']['Name'])


class BaseAction(object):
    pass


class Export(BaseAction):

    log = logging.getLogger("deployer.export")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment
        self.env_status = None
        self.env_state = {'services': {}, 'relations': {}}

    def run(self):
        pass


class Diff(BaseAction):

    log = logging.getLogger("deployer.diff")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment
        self.env_status = None
        self.env_state = {'services': {}, 'relations': []}

    def load_env(self):
        """
        """
        rels = set()
        for svc_name in self.env_status['services']:
            if not svc_name in self.env_status['services']:
                self.env_state['services'][svc_name] = 'missing'
            self.env_state['services'].setdefault(svc_name, {})[
                'options'] = self.env.get_config(svc_name)
            self.env_state['services'][svc_name][
                'constraints'] = self.env.get_constraints(svc_name)
            self.env_state['services'][svc_name][
                'unit_count'] = len(self.env_status[
                    'services'][svc_name]['units'])
            rels.update(self._load_rels(svc_name))
        self.env_state['relations'] = sorted(rels)

    def _load_rels(self, svc_name):
        rels = set()
        svc_rels = self.env_status['services'][svc_name].get(
            'relations', {})
        # There is ambiguity here for multiple rels between two
        # services without the relation id, which we need support
        # from core for.
        for r_name, r_svcs in svc_rels.items():
            for r_svc in r_svcs:
                # Skip peer relations
                if r_svc == svc_name:
                    continue
                rr_name = self._get_rel_name(svc_name, r_svc)
                rels.add(
                    tuple(sorted([
                        "%s:%s" % (svc_name, r_name),
                        "%s:%s" % (r_svc, rr_name)])))
        return rels

    def _get_rel_name(self, src, tgt):
        svc_rels = self.env_status['services'][tgt]['relations']
        found = None
        for r, eps in svc_rels.items():
            if src in eps:
                if found:
                    raise ValueError("Ambigious relations for service")
                found = r
        return found

    def get_delta(self):
        delta = {}
        rels_delta = self._get_relations_delta()
        if rels_delta:
            delta['relations'] = rels_delta
        svc_delta = self._get_services_delta()
        if svc_delta:
            delta['services'] = svc_delta
        return delta

    def _get_relations_delta(self):
        # Simple endpoint diff, no qualified endpoint checking.

        # Env relations are always qualified (at least in go).
        delta = {}
        env_rels = set(
            EndpointPair(*x) for x in self.env_state.get('relations', ()))
        dep_rels = set(
            [EndpointPair(*y) for y in self.deployment.get_relations()])

        for r in dep_rels.difference(env_rels):
            delta.setdefault('missing', []).append(r)

        for r in env_rels.difference(dep_rels):
            delta.setdefault('unknown', []).append(r)

        return delta

    def _get_services_delta(self):
        delta = {}
        env_svcs = set(self.env_status['services'].keys())
        dep_svcs = set([s.name for s in self.deployment.get_services()])

        missing = dep_svcs - env_svcs
        if missing:
            delta['missing'] = {}
        for a in missing:
            delta['missing'][a] = self.deployment.get_service(
                a).svc_data
        unknown = env_svcs - dep_svcs
        if unknown:
            delta['unknown'] = {}
        for r in unknown:
            delta['unknown'][r] = self.env_state.get(r)

        for cs in env_svcs.intersection(dep_svcs):
            d_s = self.deployment.get_service(cs).svc_data
            e_s = self.env_state['services'][cs]
            mod = self._diff_service(e_s, d_s)
            if not mod:
                continue
            if not 'modified' in delta:
                delta['modified'] = {}
            delta['modified'][cs] = mod
        return delta

    def _diff_service(self, e_s, d_s):
        mod = {}
        if 'constraints' in d_s:
            d_sc = _parse_constraints(d_s['constraints'])
            if d_sc != e_s['constraints']:
                mod['constraints'] = e_s['constraints']
        for k, v in d_s.get('options', {}).items():
            # Deploy options not known to the env may originate
            # from charm version delta or be an invalid config.
            if not k in e_s['options']:
                continue
            e_v = e_s['options'].get(k, {}).get('value')
            if e_v != v:
                mod['config'] = {k: e_v}
        if e_s['unit_count'] != d_s.get('num_units', 1):
            mod['num_units'] = e_s['num_units']
        return mod

    def run(self):
        self.start_time = time.time()
        self.env.connect()
        self.env_status = self.env.status()
        self.load_env()
        delta = self.get_delta()
        if delta:
            print yaml_dump(delta)


class Importer(BaseAction):

    log = logging.getLogger("deployer.import")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment

    def add_units(self):
        self.log.debug("Adding units...")
        # Add units to existing services that don't match count.
        env_status = self.env.status()
        added = set()
        for svc in self.deployment.get_services():
            delta = (svc.num_units -
                     len(env_status['services'][svc.name].get('units', ())))
            if delta > 0:
                charm = self.deployment.get_charm_for(svc.name)
                if charm.is_subordinate():
                    self.log.warning(
                        "Config specifies num units for subordinate: %s",
                        svc.name)
                    continue
                self.log.info(
                    "Adding %d more units to %s" % (abs(delta), svc.name))
                for u in self.env.add_units(svc.name, abs(delta)):
                    added.add(u)
            else:
                self.log.debug(
                    " Service %r does not need any more units added.",
                    svc.name)

    def get_charms(self):
        # Get Charms
        self.log.debug("Getting charms...")
        self.deployment.fetch_charms(
            update=self.options.update_charms,
            no_local_mods=self.options.no_local_mods)

        # Load config overrides/includes and verify rels after we can
        # validate them.
        self.deployment.resolve(self.options.overrides or ())

    def deploy_services(self):
        self.log.info("Deploying services...")
        env_status = self.env.status()
        for svc in self.deployment.get_services():
            if svc.name in env_status['services']:
                self.log.debug(
                    " Service %r already deployed. Skipping" % svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            self.log.info(
                " Deploying service %s using %s", svc.name, charm.charm_url)
            self.env.deploy(
                svc.name,
                charm.charm_url,
                self.deployment.repo_path,
                svc.config,
                svc.constraints,
                svc.num_units,
                svc.force_machine)

            if svc.expose:
                self.env.expose(svc.name)

            if self.options.deploy_delay:
                self.log.debug(" Waiting for deploy delay")
                time.sleep(self.options.deploy_delay)

    def add_relations(self):
        self.log.info("Adding relations...")

        # Relations
        status = self.env.status()
        created = False

        for end_a, end_b in self.deployment.get_relations():
            if self._rel_exists(status, end_a, end_b):
                continue
            self.log.info(" Adding relation %s <-> %s", end_a, end_b)
            self.env.add_relation(end_a, end_b)
            created = True
            # per the original, not sure the use case.
            self.log.debug(" Waiting 5s before next relation")
            time.sleep(5)
        return created

    def _rel_exists(self, status, end_a, end_b):
        # Checks for a named relation on one side that matches the local
        # endpoint and remote service.
        (name_a, name_b, rem_a, rem_b) = (end_a, end_b, None, None)

        if ":" in end_a:
            name_a, rem_a = end_a.split(":", 1)
        if ":" in end_b:
            name_b, rem_b = end_b.split(":", 1)

        rels_svc_a = status['services'][name_a].get('relations', {})

        found = False
        for r, related in rels_svc_a.items():
            if name_b in related:
                if rem_a and not r in rem_a:
                    continue
                found = True
                break
        if found:
            return True
        return False

    def wait_for_units(self, ignore_error=False):
        timeout = self.options.timeout - (time.time() - self.start_time)
        if timeout < 0:
            self.log.error("Reached deployment timeout.. exiting")
            raise ErrorExit()
        try:
            self.env.wait_for_units(
                int(timeout), watch=self.options.watch, no_exit=ignore_error)
        except UnitErrors:
            if not ignore_error:
                raise

    def run(self):
        self.start_time = time.time()
        self.env.connect()

        # Get charms
        self.get_charms()
        if self.options.branch_only:
            return

        self.deploy_services()
        self.wait_for_units()
        self.add_units()

        rels_created = self.add_relations()

        # Wait for the units to be up before waiting for rel stability.
        self.log.debug("Waiting for units to be started")
        self.wait_for_units(self.options.retry_count)
        if rels_created:
            self.log.debug("Waiting for relations %d", self.options.rel_wait)
            time.sleep(self.options.rel_wait)
            self.wait_for_units(self.options.retry_count)

        if self.options.retry_count:
            self.log.info("Looking for errors to auto-retry")
            self.env.resolve_errors(
                self.retry_count,
                self.options.timeout - time.time() - self.start_time)


def main():
    stime = time.time()
    try:
        run()
    except ErrorExit:
        logging.getLogger('deployer.cli').info(
            "Deployment stopped. run time: %0.2f", time.time() - stime)
        sys.exit(1)


def run():
    parser = setup_parser()
    options = parser.parse_args()

    # Debug implies watching and verbose
    if options.debug:
        options.watch = options.verbose = True
    setup_logging(options.verbose, options.debug)

    log = logging.getLogger("deployer.cli")
    start_time = time.time()

    env = select_runtime(options.juju_env)
    log.debug('Using runtime %s', env.__class__.__name__)

    config = ConfigStack(options.configs or [])

    # Destroy services and exit
    if options.destroy_services or options.terminate_machines:
        log.info("Resetting environment...")
        env.connect()
        env.reset(terminate_machines=options.terminate_machines,
                  terminate_delay=options.deploy_delay,
                  watch=options.watch)
        log.info("Environment reset in %0.2f", time.time() - start_time)
        sys.exit(0)

    # Display service info and exit
    if options.find_service:
        address = env.get_service_address(options.find_service)
        if address is None:
            log.error("Service not found %r", options.find_service)
            sys.exit(1)
        elif not address:
            log.warning("Service: %s has no address for first unit",
                        options.find_service)
        else:
            log.info("Service: %s address: %s", options.find_service, address)
        sys.exit(0)

    # Just resolve/retry hooks in the environment
    if not options.deployment and options.retry_count:
        log.info("Retrying hooks for error resolution")
        env.connect()
        env.resolve_errors(
            options.retry_count, watch=options.watch, timeout=options.timeout)

    # Arg check on config files and deployment name.
    if not options.configs:
        log.error("Config files must be specified")
        sys.exit(1)

    config.load()

    # Just list the available deployments
    if options.list_deploys:
        print "\n".join(sorted(config.keys()))
        sys.exit(0)

    # Do something to a deployment
    if not options.deployment:
        log.error(
            "Deployment name must be specified. available: %s", tuple(
                sorted(config.keys())))
        sys.exit(1)

    deployment = config.get(options.deployment)

    if options.diff:
        Diff(env, deployment, options).run()
        return

    # Import it
    log.info("Starting deployment of %s", options.deployment)
    Importer(env, deployment, options).run()

    # Deploy complete
    log.info("Deployment complete in %0.2f seconds" % (
        time.time() - start_time))

if __name__ == '__main__':

    try:
        main()
    except SystemExit:
        pass
    except:
        import pdb, traceback, sys
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
