class PushBase(object):

    def __init__(self, **data):
        self.config = data['config'][self.__class__.__name__]
        self.device_id = data['device_id']
        self.message = data['message']
        self.token = data['token']
        print("%s instantiated for device %s" % (self.__class__.__name__,
                                                 self.device_id))

    def check_token(self):
        raise NotImplementedError

    def send(self):
        raise NotImplementedError


class InvalidTokenException(Exception):

    def __init__(self, device_id, token):
        self.device_id = device_id
        self.token = token
