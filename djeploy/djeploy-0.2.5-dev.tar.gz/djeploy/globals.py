import os
from fabric.colors import red as _red
from fabric.contrib.files import exists as fab_exists
from fabric.api import *


def set_env(**kwargs):
    for k, v in kwargs.iteritems():
        setattr(env, 'djeploy_%s' % k, v)
    return kwargs


def djeploy_require(*keys, **kwargs):
    keys = map(lambda x: 'djeploy_%s' % x, keys)
    require(*keys, **kwargs)


def get_env(*keys):
    djeploy_require(*keys)
    keys = map(lambda x: 'djeploy_%s' % x, keys)
    results = {}
    for key in keys:
        results[key.replace('djeploy_', '')] = env[key]
    return results


def _is_local():
    djeploy_require('run_type')
    return env.djeploy_run_type == 'local'


def _get_callable(default=run):
    'Return local or default (run) based on hosts variable'
    is_local = _is_local()
    if default == cd:
        return lcd if is_local else default

    def _local(cmd, *args, **kwargs):
        # Ensure only capture arg is passed to local
        if 'capture' in kwargs:
            capture = kwargs.pop('capture')
        else:
            try:
                capture = bool(args[0])
            except IndexError:
                capture = False
        return local(cmd, capture=capture)
    return _local if is_local else default


def _get_cmds():
    'Return run, sudo and cd commands.'
    return (
        _get_callable(),
        _get_callable(default=sudo),
        _get_callable(default=cd),
    )


class Command(object):
    def __init__(self):
        self._is_local = False
        self._fab_settings = None
        self._clear_settings = False
        self.revert_cmds()

    def revert_cmds(self):
        self._run = run
        self._sudo = sudo
        self._cd = cd

    @property
    def is_local(self):
        self._is_local = _is_local()
        return self._is_local

    def set_cmds(self):
        self._run, self._sudo, self._cd = _get_cmds()

    def clear_local_settings(self):
        self._fab_settings = None
        self._clear_settings = False

    def set_local_settings(self, **kwargs):
        if self._fab_settings is None:
            self._fab_settings = {}
        self._fab_settings.update(kwargs)

    def build_settings(self, fab_settings):
        if fab_settings is None and self._fab_settings is None:
            return None

        tmp_fab_settings = {}
        if self._fab_settings is not None:
            tmp_fab_settings.update(self._fab_settings)
        if fab_settings is not None:
            tmp_fab_settings.update(fab_settings)
        if 'clear_after_run' in tmp_fab_settings:
            self._clear_settings = tmp_fab_settings.pop('clear_after_run')
        
        return tmp_fab_settings

    def get_settings(self, fab_settings):
        assert isinstance(fab_settings, dict)
        args = []
        kwargs = {}
        manager_map = {
            'cd': cd,
            'lcd': lcd,
            'hide': hide,
            'path': path,
            'prefix': prefix,
            'show': show,
        }

        for k, v in fab_settings.iteritems():
            if k in manager_map:
                func = manager_map[k]
                if isinstance(v, (list, tuple)):
                    args.append(func(*v))
                else:
                    args.append(func(v))
            else:
                kwargs[k] = v

        return args, kwargs

    def settings_execute(self, cmd, *args, **kwargs):
        fab_settings = self.build_settings(kwargs.pop('fab_settings', None))
        if fab_settings:
            a, k = self.get_settings(fab_settings)
            with settings(*a, **k):
                output = cmd(*args, **kwargs)
        else:
            output = cmd(*args, **kwargs)

        if self._clear_settings:
            self.clear_local_settings()
        return output

    def run(self, *args, **kwargs):
        return self.settings_execute(self._run, *args, **kwargs)

    def sudo(self, *args, **kwargs):
        return self.settings_execute(self._sudo, *args, **kwargs)

    def cd(self, *args, **kwargs):
        return self._cd(*args, **kwargs)

    def abort(self, message):
        abort(_red(message))

    def exists(self, path):
        if self.is_local:
            return os.path.exists(path)
        else:
            return fab_exists(path)


# Used everywhere...
command = Command()
