
from deployer.errors import EnvError
from deployer.relation import Endpoint
from deployer.utils import yaml_load, yaml_dump


class ProviderError(Exception):
    pass


class InternalError(Exception):
    pass


class Model(object):

    def __init__(self, db, **kw):
        self.db = db
        self.data = kw

    def __getattr__(self, k):
        if k in self.data:
            return self.data[k]
        raise AttributeError(k)

class Service(Model):

    def get_charm(self):
        return self.db.get_charm(self.charm_url)

    def provides(self):
        charm = self.get_charm()
        return charm.provides

    def requires(self):
        charm = self.get_charm()
        return charm.requires


class Unit(Model):
    pass


class Machine(Model):
    pass


class Topology(object):

    def __init__(self):
        self._state = {}

    def dump(self):
        yaml_dump(self._state)

    def parse(self, data):
        self._state = yaml_load(data)

    def add_machine(self, machine_id, **kw):
        machines = self._state.setdefault('machines', {})
        if machine_id in machines:
            raise InternalError("machine exists %s" % machine_id)
        kw['machine_id'] = machine_id
        machines[machine_id] = kw

    def get_machines(self):
        return self._machines.values()

    def remove_machine(self, machine_id):
        machines = self._state.setdefault('machines', {})
        if not machine_id in machines:
            raise InternalError("machine doesn't exist %s" % machine_id)

        machines.pop(machine_id)

    def machine_has_units(self, machine_id):
        """Return True if machine has any assigned units."""
        self._assert_machine(machine_id)
        services = self._state.get("services", self._nil_dict)
        for service in services.itervalues():
            for unit in service["units"].itervalues():
                if unit.get("machine") == machine_id:
                    return True
        return False

    def add_service(self, service_name, charm, **kw):
        services = self._state.setdefault("services", {})
        if service_name in services:
            raise InternalError(
                "Attempted to add duplicated service: %s" % service_name)
        services[service_name] = {
            "name": service_name,
            "units": {},
            "sequence": 0}

    def get_services(self):
        return self._services.values()

    def add_unit(self):
        pass

    def remove_unit(self):
        pass

    def get_units(self):
        pass

    def add_relation(self):
        pass

    def get_relations(self):
        pass

    def remove_relation(self):
        pass

    def set_constraints(self, constraints, service_name=None):
        pass

    def set_config(self, service_name, config):
        pass

    def upgrade_charm(self, service, charm_url):
        pass

    def _assert_relation(self, relation_id):
        if relation_id not in self._state.get(
                "relations", self._nil_dict):
            raise InternalError(
                "Relation not found: %s" % relation_id)

    def _assert_machine(self, machine_id):
        if machine_id not in self._state.get(
                "machines", self._nil_dict):
            raise InternalError(
                "Machine not found: %s" % machine_id)

    def _assert_service(self, service_id):
        if service_id not in self._state.get(
                "services", self._nil_dict):
            raise InternalError(
                "Service not found: %s" % service_id)

    def _assert_service_unit(self, service_id, unit_id):
        self._assert_service(service_id)
        service = self._state["services"][service_id]
        if unit_id not in service.get("units", self._nil_dict):
            raise InternalError(
                "Service unit %s not found in service %s" % (
                    unit_id, service_id))


class MemoryEnvironment(object):

    def __init__(self, topology=None, data=None):
        if topology:
            self.topology = topology
        elif data:
            self.topology = Topology()
            self.topology.parse(data)

    def add_units(self, service_name, num_units):
        """Add units
        """
        if not service_name in self.services:
            raise ProviderError("Service %s unknown" % service_name)

        svc_data = self.services[service_name]
        sequence = svc_data['unit_sequence']

        for n in range(sequence, sequence + num_units):
            uid = "%s/%s" % (service_name, n)
            self.units[uid] = {}

        svc_data['unit_sequence'] += num_units

    def _get_service(self, service_name):
        if not service_name in self.data['services']:
            raise EnvError("Invalid service name")
        idx = self.data['services'][service_name]['unit_sequence']
        return idx

    def add_relation(self, endpoint_a, endpoint_b):
        """Add relations
        """
        if not Endpoint(endpoint_a).service in self.services:
            raise ProviderError("Service %s unknown" % endpoint_a)

    def close(self):
        """
        """

    def connect(self):
        """
        """
        return self

    def get_config(self, service_name):
        if not service_name in self.services:
            raise ProviderError("Service %s unknown" % service_name)

    def get_constraints(self, service_name):
        if not service_name in self.services:
            raise ProviderError("Service %s unknown" % service_name)

    def get_cli_status(self):
        pass

    def reset(self):
        pass

    def resolve_errors(self, retry_count=0, timeout=600, watch=False, delay=5):
        pass

    def status(self):
        pass

    def wait_for_units(
            self, timeout, goal_state="started", watch=False, no_exit=False):
        pass
