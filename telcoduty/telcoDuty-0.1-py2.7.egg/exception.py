__author__ = 'alexey.grachev'


class Exception(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message

    def message(self):
        return self.message