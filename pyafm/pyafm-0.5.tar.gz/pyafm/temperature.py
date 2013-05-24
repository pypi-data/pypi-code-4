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

from scipy.constants import C2K as _C2K
from pypid.backend.melcor import MelcorBackend as _TemperatureBackend

from . import LOG as _LOG
from .config import Celsius, Kelvin


class Temperature (object):
    """A temperature monitor based on the Melcor controller.

    >>> from pyafm.config import TemperatureConfig

    >>> config = TemperatureConfig()
    >>> t = Temperature(config=config)
    >>> t.load_from_config()
    >>> t.get_temperature()  # doctest: +SKIP
    297.37
    >>> t.cleanup()
    """
    def __init__(self, config, backend=None):
        _LOG.debug('setup temperature monitor')
        self.config = config
        self.backend = backend

    def load_from_config(self):
        c = self.config  # reduce verbosity
        if self.backend is None:
            self.backend = _TemperatureBackend(
                controller=c['controller'],
                device=c['device'],
                baudrate=c['baudrate'])
            self.backend.set_max_mv(max=c['max-current'])  # amp
        self.name = self.config['name']

    def setup_config(self):
        self.config['controller'] = self.backend._controller
        self.config['device'] = self.backend._client.port
        self.config['baudrate'] = self.backend._client.baudrate
        self.config['max-current'] = self.backend.get_max_mv()

    def cleanup(self):
        try:
            self.backend.cleanup()
        except Exception:
            pass
        self.backend = None

    def get_temperature(self):
        temp = self.backend.get_pv()
        unit = self.config['units']
        if unit == Kelvin:  # convert K -> K
            pass
        elif unit == Celsius:  # convert C -> K
            temp = _C2K(temp)
        else:
            raise NotImplementedError(unit)
        _LOG.info('measured temperature of {:g} K'.format(temp))
        return temp
