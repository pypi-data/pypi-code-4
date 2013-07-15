import gcm
from push import InvalidTokenException, PushBase


class C2DM(PushBase):

    def send(self):
        pass


class GCM(PushBase):

    def __init__(self, **data):
        super(GCM, self).__init__(**data)
        self.gcm = gcm.GCM(self.config['API_KEY'])

    def send(self):
        try:
            return self.gcm.plaintext_request(
                registration_id=self.token,
                data={'message': self.message}
            )
        except (gcm.gcm.GCMNotRegisteredException, gcm.gcm.GCMInvalidRegistrationException):
            print("Registration ID %s is invalid" % self.token)
            raise InvalidTokenException(self.device_id, self.token)
