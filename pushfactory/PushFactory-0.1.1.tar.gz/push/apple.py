from pyapns import configure, provision, notify
from push import PushBase


class APN(PushBase):

    def __init__(self, **data):
        super(APN, self).__init__(**data)
        self.badge = data['badge']
        try:
            self.message_data = data['message_data']
        except KeyError:
            self.message_data = False
        configure(data['config']['PYAPNS'])
        provision(self.config['provision'], open(
            self.config['certfile']).read(), self.config['environment'])

    def check_token():
        pass

    def send(self):
        notify(self.config['provision'], self.token, ({
            'aps': {
                'alert': self.message,
                'badge': self.badge,
                'sound': self.config['sound'],
                'message_data': self.message_data,
            }
        }))
