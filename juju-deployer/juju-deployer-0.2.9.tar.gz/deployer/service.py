class Service(object):

    def __init__(self, name, svc_data):
        self.svc_data = svc_data
        self.name = name

    def __repr__(self):
        return "<Service %s>" % (self.name)

    @property
    def annotations(self):
        a = self.svc_data.get('annotations')
        if a is None:
            return a
        # core annotations only supports string key / values
        d = {}
        for k, v in a.items():
            d[str(k)] = str(v)
        return d

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
    def unit_placement(self):
        # Separate checks to support machine 0 placement.
        value = self.svc_data.get('to')
        if value is None:
            value = self.svc_data.get('force-machine')
        if value is not None and not isinstance(value, list):
            value = [value]
        return value or []

    @property
    def expose(self):
        return self.svc_data.get('expose', False)
