# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
#
# This file is part of pyafm.
#
# pyafm is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pyafm is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pyafm.  If not, see <http://www.gnu.org/licenses/>.

from pycomedi.channel import DigitalChannel as _DigitalChannel
import pypiezo.base as _base


class DigitalPort (object):
    """A digital input/output port (i.e. cluster of channels).

    >>> from pyafm.config import DigitalPortConfig

    >>> devices = []

    >>> config = DigitalPortConfig()
    >>> config['channels'] = [1, 2, 3, 4]
    >>> config['name'] = 'test port'

    >>> port = DigitalPort(config=config)
    >>> port.load_from_config(devices=devices)
    >>> port.write_bitfield(13)
    >>> port.write([1, 0, 1, 0])
    >>> port.write_bitfield(0)

    >>> for device in devices:
    ...     device.close()
    """
    def __init__(self, config):
        self.config = config
        self.subdevice = None

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if self.subdevice is None:
            device = _base.load_device(filename=c['device'], devices=devices)
            if c['subdevice'] < 0:
                self.subdevice = device.find_subdevice_by_type(
                    c['subdevice-type'])
            else:
                self.subdevice = device.subdevice(index=c['subdevice'])
            self.channels = []
            self.write_mask = 0
            for index in c['channels']:
                channel = self.subdevice.channel(
                    index=index, factory=_DigitalChannel)
                channel.dio_config(c['direction'])
                self.write_mask |= 1 << index
                self.channels.append(channel)
        self.name = c['name']

    def setup_config(self):
        self.config['device'] = self.subdevice.device.filename
        self.config['subdevice'] = self.subdevice.index
        self.config['channels'] = [c.index for c in self.channels]
        if self.channels:
            self.config['direction'] = self.channels[0].dio_get_config()

    def write(self, values):
        value = 0
        for channel,val in zip(self.channels, values):
            value &= val * (1 << channel.index)
        self.write_bitfield(value)

    def write_bitfield(self, value):
        self.subdevice.dio_bitfield(bits=value, write_mask=self.write_mask)
