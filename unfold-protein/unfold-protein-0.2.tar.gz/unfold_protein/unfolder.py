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

"""Define classes for carrying out an unfolding cycle with an AFM."""

from __future__ import division

import email.utils as _email_utils
import os.path as _os_path
import time as _time

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
from h5config.storage.hdf5 import h5_create_group as _h5_create_group
import h5py as _h5py
import pyafm.afm as _pyafm_afm
import pypiezo.base as _pypiezo_base

from . import LOG as _LOG
from . import package_config as _package_config

try:
    import numpy as _numpy
    import matplotlib as _matplotlib
    from matplotlib import pyplot as _pyplot
    _pyplot.ion()
    FIGURE = _pyplot.figure()
except (ImportError, RuntimeError), _matplotlib_import_error:
    _pyplot = None
#    from pylab import figure, plot, title, legend, hold, subplot, draw


class ExceptionTooClose (Exception):
    """
    The piezo is too close to the surface.
    """
    pass

class ExceptionTooFar (Exception):
    """
    The piezo is too far from the surface.
    """
    pass


class Unfolder (object):
    def __init__(self, config=None, afm=None):
        self.config = config
        self.afm = afm
        if self.afm:
            self.zero_piezo()

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if self.afm is None and c['afm']:
            self.afm = _pyafm_afm.AFM(config=c['afm'])
            self.afm.load_from_config(devices=devices)

    def setup_config(self):
        if self.afm:
            self.afm.setup_config()
            self.config['afm'] = self.afm.config
        else:
            self.config['afm'] = None

    def run(self):
        """Approach-bind-unfold-save[-plot] cycle.
        """
        ret = {}
        ret['timestamp'] = _email_utils.formatdate(localtime=True)
	ret['temperature'] = self.afm.get_temperature()
        ret['approach'] = self._approach()
        self._bind()
        ret['unfold'] = self._unfold()
        self._save(**ret)
        if _package_config['matplotlib']:
            self._plot(**ret)
        return ret

    def _approach(self):
        """Approach the surface using the piezo

        Steps in until a given setpoint is reached.
        """
        config = self.config['approach']
        deflection = self.read_deflection()
        setpoint = deflection + config['relative setpoint']
        _LOG.info('approach with setpoint = {}'.format(setpoint))
        axis_config = self.afm.piezo.config.select_config(
                'axes', self.afm.config['main-axis'],
                get_attribute=_pypiezo_base.get_axis_name
                )
        def_config = self.afm.piezo.config.select_config(
            'inputs', 'deflection')
        start_pos = self.afm.piezo.last_output[self.afm.config['main-axis']]

        # calculate parameters for move_to_pos_or_def from config
        setpoint_bits = _pypiezo_base.convert_volts_to_bits(
            def_config, setpoint)
        mid_pos_bits = _pypiezo_base.convert_meters_to_bits(
            axis_config, 0)
        step_pos_bits = _pypiezo_base.convert_meters_to_bits(
            axis_config, config['step'])
        step_bits = step_pos_bits - mid_pos_bits
        frequency = config['velocity'] / config['step']

        # run the approach
        data = self.afm.piezo.move_to_pos_or_def(
            axis_name=self.afm.config['main-axis'], deflection=setpoint_bits,
            step=step_bits, frequency=frequency, return_data=True)
        data['setpoint'] = setpoint
        # check the output
        if data['deflection'].max() < setpoint_bits:
            _LOG.info(('unfolding too far from the surface '
                       '(def {} < target {})').format(
                        data['deflection'].max(), setpoint_bits))
            self.afm.piezo.jump(self.afm.config['main-axis'], start_pos)
            if _package_config['matplotlib']:
                print data
                FIGURE.clear()
                axes = FIGURE.add_subplot(1, 1, 1)
                axes.plot(data['z'], data['deflection'], label='Approach')
                axes.set_title('Unfolding too far')
                FIGURE.canvas.draw()
                if hasattr(FIGURE, 'show'):
                    FIGURE.show()
                if not _matplotlib.is_interactive():
                    _pyplot.show()
            _LOG.debug('raising ExceptionTooFar')
            raise ExceptionTooFar
        return data

    def _bind(self):
        """Wait on the surface while the protein binds."""
        time = self.config['bind time']
        _LOG.info('binding for {:.3f} seconds'.format(time))
        _time.sleep(time)

    def _unfold(self):
        """Pull the bound protein, forcing unfolding events."""
        config = self.config['unfold']
        velocity = config['velocity']
        _LOG.info('unfold at {:g} m/s'.format(velocity))
        axis = self.afm.piezo.axis_by_name(self.afm.config['main-axis'])
        axis_config = self.afm.piezo.config.select_config(
                'axes', self.afm.config['main-axis'],
                get_attribute=_pypiezo_base.get_axis_name
                )
        d = self.afm.piezo.channel_by_name('deflection')
        def_config = self.afm.piezo.config.select_config(
            'inputs', 'deflection')
        start_pos = self.afm.piezo.last_output[self.afm.config['main-axis']]

        start_pos_m = _pypiezo_base.convert_bits_to_meters(
            axis_config, start_pos)
        final_pos_m = start_pos_m - config['distance']
        final_pos = _pypiezo_base.convert_meters_to_bits(
            axis_config, final_pos_m)
        dtype = self.afm.piezo.channel_dtype(
            self.afm.config['main-axis'], direction='output')
        frequency = config['frequency']
        num_steps = int(
            config['distance'] / config['velocity'] * frequency) + 1
        #   (m)                * (s/m)              * (samples/s)
        max_samples = self._get_max_samples()
        if num_steps > max_samples:
            num_steps = max_samples
            frequency = (num_steps - 1)*config['velocity']/config['distance']
            _LOG.info(('limit frequency to {} Hz (from {} Hz) to fit in DAQ '
                       'card buffer').format(frequency, config['frequency']))

        out = _numpy.linspace(
            start_pos, final_pos, num_steps).astype(dtype)
        # TODO: check size of output buffer.
        out = out.reshape((len(out), 1))
        _LOG.debug(
            'unfolding from {} to {} in {} steps at {} Hz'.format(
                start_pos, final_pos, num_steps, frequency))
        data = self.afm.piezo.ramp(
            data=out, frequency=frequency, output_names=[self.afm.config['main-axis']],
            input_names=['deflection'])
        return {
            'frequency': frequency, self.afm.config['main-axis']:out, 'deflection':data}

    def _get_max_samples(self):
        """Return the maximum number of samples that will fit on the card.

        `pycomedi.utility.Writer` seems to have trouble when the the
        output buffer is bigger than the card's onboard memory, so
        we reduce the frequency if neccessary to fit the scan in
        memory.
        """
        axis = self.afm.piezo.axis_by_name(self.afm.config['main-axis'])
        buffer_size = axis.axis_channel.subdevice.get_buffer_size()
        dtype = self.afm.piezo.channel_dtype(
            self.afm.config['main-axis'], direction='output')
        # `channel_dtype` returns `numpy.uint16`, `numpy.uint32`,
        # etc., which are "generic types".  We use `numpy.dtype` to
        # construct a `dtype` object:
        #   >>> import numpy
        #   >>> numpy.uint16
        #   <type 'numpy.uint16'>
        #   >>> numpy.dtype(numpy.uint16)
        #   dtype('uint16')
        dt = _numpy.dtype(dtype)
        sample_size = dt.itemsize
        max_output_samples = buffer_size // sample_size
        return max_output_samples

    def _save(self, temperature, approach, unfold, timestamp):
        config = self.config['save']
        time_tuple = _email_utils.parsedate(timestamp)
        filename = _os_path.join(
            config['base directory'],
            '{0}-{1:02d}-{2:02d}T{3:02d}-{4:02d}-{5:02d}.h5'.format(
                *time_tuple))
        _LOG.info('saving {}'.format(filename))
        with _h5py.File(filename, 'a') as f:
            storage = _HDF5_Storage()
            config_cwg = _h5_create_group(f, 'config')
            storage.save(config=self.config, group=config_cwg)
            f['/environment/timestamp'] = timestamp
            x_axis_name = 'x'
            f['/environment/{}-position/data'.format(x_axis_name)
              ] = self.afm.piezo.last_output[x_axis_name]
            if temperature is not None:
                f['/environment/temperature'] = temperature
            for k,v in approach.items():
                f['approach/{}'.format(k)] = v
            for k,v in unfold.items():
                f['unfold/{}'.format(k)] = v

    def _plot(self, temperature, approach, unfold, timestamp):
        "Plot the unfolding cycle"
        if not _pyplot:
            raise _matplotlib_import_error
        FIGURE.clear()
        axes = FIGURE.add_subplot(1, 1, 1)
        axes.hold(True)
        axes.plot(approach['z'], approach['deflection'], label='Approach')
        axes.plot(unfold['z'], unfold['deflection'], label='Unfold')
        axes.legend(loc='best')
        axes.set_title('Unfolding')
        FIGURE.canvas.draw()
        if hasattr(FIGURE, 'show'):
            FIGURE.show()
        if not _matplotlib.is_interactive():
            _pyplot.show()

    def zero_piezo(self):
        _LOG.info('zero piezo')
        x_mid_pos = _pypiezo_base.convert_volts_to_bits(
            self.afm.piezo.config.select_config(
                'axes', 'x', get_attribute=_pypiezo_base.get_axis_name
                )['channel'],
            0)
        z_mid_pos = _pypiezo_base.convert_volts_to_bits(
            self.afm.piezo.config.select_config(
                'axes', 'z', get_attribute=_pypiezo_base.get_axis_name
                )['channel'],
            0)
        self.afm.piezo.jump('z', z_mid_pos)
        self.afm.piezo.jump('x', x_mid_pos)

    def read_deflection(self):
        bits = self.afm.piezo.read_deflection()
        return _pypiezo_base.convert_bits_to_volts(
            self.afm.piezo.config.select_config('inputs', 'deflection'), bits)
