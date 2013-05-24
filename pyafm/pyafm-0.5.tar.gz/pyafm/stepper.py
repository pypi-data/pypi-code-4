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

from __future__ import absolute_import

import stepper as _stepper
from .digital_port import DigitalPort as _DigitalPort


class Stepper(_stepper.Stepper):
    """Extend `stepper.Stepper` for easy configuration via `h5config`.

    Uses `DigitalPort` for transmitting the output.

    >>> from pycomedi import constant as _constant
    >>> from pyafm.config import StepperConfig, DigitalPortConfig

    >>> devices = []

    >>> config = StepperConfig()
    >>> config['port'] = DigitalPortConfig()
    >>> config['port']['channels'] = [1, 2, 3, 4]
    >>> config['port']['direction'] = _constant.IO_DIRECTION.output
    >>> config['port']['name'] = 'stepper port'
    >>> config['name'] = 'test stepper'

    >>> s = Stepper(config=config)
    >>> s.load_from_config(devices=devices)
    >>> s.position
    0
    >>> s.single_step(1)
    >>> s.position
    2

    >>> for device in devices:
    ...     device.close()
    """
    def __init__(self, config):
        self.config = config
        self.port = None
        c = self.config  # reduce verbosity
        dummy_write = lambda value: None
        super(Stepper, self).__init__(
            write=dummy_write, full_step=c['full-step'], logic=c['logic'],
            delay=c['delay'], step_size=c['step-size'], backlash=c['backlash'])

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if self.port is None:
            self.port = _DigitalPort(config=c['port'])
            self.port.load_from_config(devices=devices)
        self._write = self.port.write_bitfield
        self.full_step = c['full-step']
        self.logic = c['logic']
        self.delay = c['delay']
        self.step_size = c['step-size']
        self.backlash = c['backlash']

    def setup_config(self):
        self.port.setup_config()
        self.config['port'] = self.port.config
        self.config['full-step'] = self.full_step
        self.config['logic'] = self.logic
        self.config['delay'] = self.delay
        self.config['step-size'] = self.step_size
        self.config['backlash'] = self.backlash
