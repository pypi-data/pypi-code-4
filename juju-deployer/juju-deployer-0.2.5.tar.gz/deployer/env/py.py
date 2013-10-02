import time

from deployer.errors import UnitErrors
from deployer.utils import ErrorExit

from .base import BaseEnvironment


class PyEnvironment(BaseEnvironment):

    def __init__(self, name, options=None):
        self.name = name
        self.options = options

    def add_units(self, service_name, num_units):
        params = self._named_env(["juju", "add-unit"])
        if num_units > 1:
            params.extend(["-n", str(num_units)])
        params.append(service_name)
        self._check_call(
            params, self.log, "Error adding units to %s", service_name)

    def add_relation(self, endpoint_a, endpoint_b):
        params = self._named_env(["juju", "add-relation"])
        params.extend([endpoint_a, endpoint_b])
        self._check_call(
            params, self.log, "Error adding relation to %s %s",
            endpoint_a, endpoint_b)

    def close(self):
        """ NoOp """

    def connect(self):
        """ NoOp """

    def _destroy_service(self, service_name):
        params = self._named_env(["juju", "destroy-service"])
        params.append(service_name)
        self._check_call(
            params, self.log, "Error destroying service %s" % service_name)

    def get_config(self, svc_name):
        params = self._named_env(["juju", "get"])
        params.append(svc_name)
        return self._check_call(
            params, self.log, "Error retrieving config for %r", svc_name)

    def get_constraints(self, svc_name):
        params = self._named_env(["juju", "get-constraints"])
        params.append(svc_name)
        return self._check_call(
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
