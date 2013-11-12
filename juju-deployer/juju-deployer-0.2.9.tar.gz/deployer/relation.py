import yaml


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
