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
        return self.svc_data.get('to') or self.svc_data.get(
            'force-machine')

    @property
    def expose(self):
        return self.svc_data.get('expose', False)
