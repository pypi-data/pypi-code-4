# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
#
# This file is part of unfold_protein.
#
# unfold_protein is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# unfold_protein is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# unfold_protein.  If not, see <http://www.gnu.org/licenses/>.

"""Define `UnfoldScanner` for sequential unfolding experiments."""

import signal as _signal

import pypiezo.base as _pypiezo_base

from . import LOG as _LOG
from . import unfolder as _unfolder
from .unfolder import ExceptionTooFar as _ExceptionTooFar
from .unfolder import ExceptionTooClose as _ExceptionTooClose


class UnfoldScanner (object):
    def __init__(self, config=None, unfolder=None):
        self.config = config
        self.unfolder = unfolder
        self._state = {'x direction': 1}

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if self.unfolder is None and c['unfold']:
            self.unfolder = _unfolder.Unfolder(config=c['unfold'])
            self.unfolder.load_from_config(devices=devices)

    def setup_config(self):
        if self.unfolder:
            self.unfolder.setup_config()
            self.config['unfolder'] = self.unfolder.config
        else:
            self.config['unfolder'] = None

    def run(self, stepper_tweaks=True):
        self._stop = False
        _signal.signal(_signal.SIGTERM, self._handle_stop_signal)
        self.unfolder.afm.move_away_from_surface()
        self.stepper_approach()
        for i in range(self.config['velocity']['num loops']):
            _LOG.info('on loop {} of {}'.format(
                    i, self.config['velocity']['num loops']))
            for velocity in self.config['velocity']['unfolding velocities']:
                if self._stop:
                    return
                self.unfolder.config['unfold']['velocity'] = velocity
                try:
                    self.unfolder.run()
                except _unfolder.ExceptionTooFar:
                    if stepper_tweaks:
                        self.stepper_approach()
                    else:
                        raise
                except _unfolder.ExceptionTooClose:
                    if stepper_tweaks:
                        self.afm.move_away_from_surface()
                        self.stepper_approach()
                    else:
                        raise
                else:
                    self.position_scan_step()

    def _handle_stop_signal(self, signal, frame):
        self._stop = True

    def stepper_approach(self):
        config = self.unfolder.config['approach']
        deflection = self.unfolder.read_deflection()
        setpoint = deflection + config['relative setpoint']
        def_config = self.unfolder.afm.piezo.config.select_config(
            'inputs', 'deflection')
        setpoint_bits = _pypiezo_base.convert_volts_to_bits(
            def_config, setpoint)
        self.unfolder.afm.stepper_approach(target_deflection=setpoint_bits)

    def position_scan_step(self):
        axis_name = 'x'
        config = self.config['position'] 
        axis_config = self.unfolder.afm.piezo.config.select_config(
                'axes', self.unfolder.afm.config['main-axis'],
                get_attribute=_pypiezo_base.get_axis_name
                )
        pos = self.unfolder.afm.piezo.last_output[axis_name]
        pos_m = _pypiezo_base.convert_bits_to_meters(axis_config, pos)
        # HACK
        try:
            step = float(open('/home/wking/x-step', 'r').read())
            _LOG.info('read step from file: {}'.format(step))
        except Exception, e:
            _LOG.warn('could not read step from file: {}'.format(e))
            step = config['x step']
        next_pos_m = pos_m + self._state['x direction']*step
        if next_pos_m > config['x max']:
            self._state['x direction'] = -1
            next_pos_m = pos_m + self._state['x direction']*step
        elif next_pos_m < config['x min']:
            self._state['x direction'] = 1
            next_pos_m = pos_m + self._state['x direction']*step
        next_pos = _pypiezo_base.convert_meters_to_bits(
            axis_config, next_pos_m)
        _LOG.info('move {} from {:g} to {:g} bits'.format(
                axis_name, pos, next_pos))
        self.unfolder.afm.piezo.jump(axis_name, next_pos)
