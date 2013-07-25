import time
import random
from nose.tools import eq_
from gadgets.devices.heater.triggers.temperature import TemperatureTrigger
from gadgets import Addresses, Sockets, Broker

class TestTemperatureTrigger(object):

    def setup(self):
        port = random.randint(5000, 50000)
        self.addresses = Addresses(in_port=port, out_port=port+1, req_port=port+2)
        comparitor = lambda x, y: x >= y
        self.trigger = TemperatureTrigger(
            'tank',
            'heat tank',
            'stop heating tank',
            {'units': 'C', 'value': 88},
            self.addresses,
            comparitor
        )

    def test_create(self):
        eq_(self.trigger._target_temperature, 88)

    def test_run(self):
        b = Broker(self.addresses)
        b.start()
        time.sleep(1)
        self.trigger.start()
        sockets = Sockets(self.addresses, ['completed heat tank'])
        sockets.send('update temperature', {'tank': {'input': {'temperature': {'value': 87, 'units': 'C'}}}})
        time.sleep(0.1)
        sockets.send('update temperature', {'tank': {'input': {'temperature': {'value': 88, 'units': 'C'}}}})
        time.sleep(0.1)
        event, message = sockets.recv()
        eq_(event, 'completed heat tank')
        sockets.send('shutdown')
        sockets.close()
