import serial

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__all__ = ["Client"]

class Client(object):
    def __init__(self, **kwargs):
        self.hdl = serial.Serial(**kwargs)

    def __call__(self, command):
        command.encode(self.hdl)
        return command.decode(self.hdl)

