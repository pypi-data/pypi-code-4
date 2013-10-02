

class MemoryEnvironment(object):

    def __init__(self):
        self.data = {}

    def add_units(self, service_name, num_units):
        """Add units
        """
        for n in range(num_units):
            self.data['services'][service_name]

    def _get_service(self, service_name):
        if not service_name in self.data['services']:
            raise EnvError("Invalid service name")
        idx = self.data['services'][service_name]['unit_sequence']
        return

    def add_relation(self, endpoint_a, endpoint_b):
        """Add relations
        """

    def close(self):
        """
        """

    def connect(self):
        """
        """

    def get_config(self, svc_name):
        pass

    def get_constraints(self, svc_name):
        pass

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
