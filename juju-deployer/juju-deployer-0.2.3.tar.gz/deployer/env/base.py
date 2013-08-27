import logging

from ..utils import (
    _get_juju_home, path_join, yaml_load, ErrorExit, yaml_dump, temp_file,
    _check_call)


class BaseEnvironment(object):

    log = logging.getLogger("deployer.env")

    @property
    def env_config_path(self):
        jhome = _get_juju_home()
        env_config_path = path_join(jhome, 'environments.yaml')
        return env_config_path

    def _check_call(self, *args, **kwargs):
        if self.options and self.options.retry_count:
            kwargs['max_retry'] = self.options.retry_count
        return _check_call(*args, **kwargs)

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
            self._check_call(
                params, self.log, "Error deploying service %r", name)

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
            self._check_call(
                params, self.log, "Error terminating machine %r" % mid)
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
            output = self._check_call(
                params, self.log, "Error getting status, is it bootstrapped?",
                stderr=fh)
        status = yaml_load(output)
        return status
