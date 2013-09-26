from construct import *

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__all__ = ["Command", "Reset", "Frequency", "WRate", "Bandwidth", "Deviation", "Power", "Rate", "Config"]

class Command(object):
    def __init__(self, request, response, **kwargs):
        self.request = request
        self.response = response
        self.kwargs = kwargs

    def encode(self, stream):
        return self.request.build_stream(Container(**(self.kwargs)), stream)

    def decode(self, stream):
        return self.response.parse_stream(stream)

class PowerAdapter(Adapter):
    power = [1,2,5,8,11,14,17,20]
    def _decode(self, obj, ctx):
        return PowerAdapter.power[obj]
    def _encode(self, obj, ctv):
        tmp = [i for (i,x) in enumerate(PowerAdapter.power) if x >= obj]
        if len(tmp):
            return tmp[0]
        return len(PowerAdapter.power)-1

frequency = UBInt32("frequency")
wrate     = UBInt32("wrate")
bandwidth = UBInt16("bandwidth")
deviation = UBInt8("deviation")
power     = PowerAdapter(UBInt8("power"))
rate      = UBInt32("rate")

no_response = Struct("ok", Magic('OK\r\n'))
header = Magic('\xAA\xFA')

config = Struct("config", frequency, wrate, bandwidth, deviation, power, rate)

def make_command(magic, *fields):
    class Req(Command):
        def __init__(self, **kwargs):
            req = Struct("request", header, Magic(magic), *fields)
            super(Req, self).__init__(req, no_response, **kwargs)
    return Req

Reset     = make_command('\xF0')
Frequency = make_command('\xD2', frequency)
WRate     = make_command('\xC3', wrate)
Bandwidth = make_command('\xB4', bandwidth)
Deviation = make_command('\xA5', deviation)
Power     = make_command('\x96', power)
Rate      = make_command('\x1E', rate)

class Config(Command):
    def __init__(self):
        req = Struct("config", header, Magic('\xE1'))
        super(Config, self).__init__(req, config)

