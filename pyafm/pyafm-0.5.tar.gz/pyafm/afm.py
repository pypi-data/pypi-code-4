# Copyright (C) 2011-2012 W. Trevor King <wking@tremily.us>
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

"""Tools for controlling atomic force microscopes.

Provides control of AFM postition using both short-range (piezo) and
long range (stepper) vertical positioning.  There are separate modules
for controlling the piezo (`pypiezo`) and stepper (`stepper`), this
module only contains methods that require the capabilities of both.
"""

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from pypiezo.afm import AFMPiezo as _AFMPiezo
from pypiezo.base import convert_bits_to_meters as _convert_bits_to_meters
from pypiezo.base import convert_meters_to_bits as _convert_meters_to_bits
from pypiezo.base import convert_volts_to_bits as _convert_volts_to_bits
from pypiezo.surface import FlatFit as _FlatFit
from pypiezo.surface import SurfaceError as _SurfaceError

from . import LOG as _LOG
from . import package_config as _package_config
from .stepper import Stepper as _Stepper
from .temperature import Temperature as _Temperature


class AFM (object):
    """Atomic force microscope positioning.

    Uses a short range `piezo` and a long range `stepper` to position
    an AFM tip relative to the surface.

    Parameters
    ----------
    piezo | pypiezo.afm.AFMpiezo instance
        Fine positioning and deflection measurements.
    stepper | stepper.Stepper instance
        Coarse positioning.
    temperature | temperature.Controller instance or None
        Optional temperature monitoring and control.

    >>> import os
    >>> import tempfile
    >>> from pycomedi import constant
    >>> import pypiezo.config
    >>> import pyafm.config
    >>> import pyafm.storage
    >>> from h5config.storage.hdf5 import pprint_HDF5

    >>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='pyafm-')
    >>> os.close(fd)

    >>> devices = []

    >>> config = pyafm.config.AFMConfig()
    >>> config['piezo'] = pypiezo.config.PiezoConfig()
    >>> config['piezo']['name'] = 'test piezo'
    >>> config['piezo']['axes'] = [pypiezo.config.AxisConfig()]
    >>> config['piezo']['axes'][0]['channel'] = (
    ...     pypiezo.config.OutputChannelConfig())
    >>> config['piezo']['axes'][0]['channel']['name'] = 'z'
    >>> config['piezo']['inputs'] = [pypiezo.config.InputChannelConfig()]
    >>> config['piezo']['inputs'][0]['name'] = 'deflection'
    >>> config['stepper'] = pyafm.config.StepperConfig()
    >>> config['stepper']['port'] = pyafm.config.DigitalPortConfig()
    >>> config['stepper']['port']['channels'] = [1, 2, 3, 4]
    >>> config['stepper']['port']['direction'] = constant.IO_DIRECTION.output
    >>> config['stepper']['port']['name'] = 'stepper port'
    >>> config['stepper']['name'] = 'test stepper'
    >>> config['temperature'] = pyafm.config.TemperatureConfig()
    >>> config['temperature']['name'] = 'test temperature'

    >>> afm = AFM(config=config)
    >>> afm.load_from_config(devices=devices)
    >>> afm.setup_config()

    >>> afm.get_temperature()  # doctest: +SKIP
    297.37

    >>> print(afm.config.dump())  # doctest: +REPORT_UDIFF
    name: 
    main-axis: 
    piezo:
      name: test piezo
      axes:
        0:
          gain: 1.0
          sensitivity: 1.0
          minimum: -10.0
          maximum: 10.0
          channel:
            name: z
            device: /dev/comedi0
            subdevice: 1
            channel: 0
            maxdata: 65535
            range: 0
            analog-reference: ground
            conversion-coefficients: -10.0,0.000305180437934
            conversion-origin: 0.0
            inverse-conversion-coefficients: 0.0,3276.75
            inverse-conversion-origin: -10.0
          monitor: 
      inputs:
        0:
          name: deflection
          device: /dev/comedi0
          subdevice: 0
          channel: 0
          maxdata: 65535
          range: 0
          analog-reference: ground
          conversion-coefficients: -10.0,0.000305180437934
          conversion-origin: 0.0
          inverse-conversion-coefficients: 0.0,3276.75
          inverse-conversion-origin: -10.0
    stepper:
      name: test stepper
      full-step: yes
      logic: yes
      delay: 0.01
      step-size: 1.7e-07
      backlash: 100
      port:
        name: stepper port
        device: /dev/comedi0
        subdevice: 2
        subdevice-type: dio
        channels: 1,2,3,4
        direction: output
    temperature:
      name: test temperature
      units: Celsius
      controller: 1
      device: /dev/ttyS0
      baudrate: 9600
      max-current: 0.0
    fallback-temperature: 295.15
    far: 3e-05

    >>> pyafm.storage.save_afm(afm=afm, filename=filename)
    >>> pprint_HDF5(filename=filename)  # doctest: +REPORT_UDIFF
    /
      <HDF5 dataset "fallback-temperature": shape (), type "<f8">
        295.15
      <HDF5 dataset "far": shape (), type "<f8">
        3e-05
      <HDF5 dataset "main-axis": shape (), type "|S1">
    <BLANKLINE>
      <HDF5 dataset "name": shape (), type "|S1">
    <BLANKLINE>
      /piezo
        /piezo/axes
          /piezo/axes/0
            /piezo/axes/0/channel
              <HDF5 dataset "analog-reference": shape (), type "|S6">
                ground
              <HDF5 dataset "channel": shape (), type "<i4">
                0
              <HDF5 dataset "conversion-coefficients": shape (2,), type "<f8">
                [ -1.00000000e+01   3.05180438e-04]
              <HDF5 dataset "conversion-origin": shape (), type "<f8">
                0.0
              <HDF5 dataset "device": shape (), type "|S12">
                /dev/comedi0
              <HDF5 dataset "inverse-conversion-coefficients": shape (2,), type "<f8">
                [    0.    3276.75]
              <HDF5 dataset "inverse-conversion-origin": shape (), type "<f8">
                -10.0
              <HDF5 dataset "maxdata": shape (), type "<i8">
                65535
              <HDF5 dataset "name": shape (), type "|S1">
                z
              <HDF5 dataset "range": shape (), type "<i4">
                0
              <HDF5 dataset "subdevice": shape (), type "<i4">
                1
            <HDF5 dataset "gain": shape (), type "<f8">
              1.0
            <HDF5 dataset "maximum": shape (), type "<f8">
              10.0
            <HDF5 dataset "minimum": shape (), type "<f8">
              -10.0
            <HDF5 dataset "monitor": shape (), type "|S1">
    <BLANKLINE>
            <HDF5 dataset "sensitivity": shape (), type "<f8">
              1.0
        /piezo/inputs
          /piezo/inputs/0
            <HDF5 dataset "analog-reference": shape (), type "|S6">
              ground
            <HDF5 dataset "channel": shape (), type "<i4">
              0
            <HDF5 dataset "conversion-coefficients": shape (2,), type "<f8">
              [ -1.00000000e+01   3.05180438e-04]
            <HDF5 dataset "conversion-origin": shape (), type "<f8">
              0.0
            <HDF5 dataset "device": shape (), type "|S12">
              /dev/comedi0
            <HDF5 dataset "inverse-conversion-coefficients": shape (2,), type "<f8">
              [    0.    3276.75]
            <HDF5 dataset "inverse-conversion-origin": shape (), type "<f8">
              -10.0
            <HDF5 dataset "maxdata": shape (), type "<i8">
              65535
            <HDF5 dataset "name": shape (), type "|S10">
              deflection
            <HDF5 dataset "range": shape (), type "<i4">
              0
            <HDF5 dataset "subdevice": shape (), type "<i4">
              0
        <HDF5 dataset "name": shape (), type "|S10">
          test piezo
      /stepper
        <HDF5 dataset "backlash": shape (), type "<i4">
          100
        <HDF5 dataset "delay": shape (), type "<f8">
          0.01
        <HDF5 dataset "full-step": shape (), type "|b1">
          True
        <HDF5 dataset "logic": shape (), type "|b1">
          True
        <HDF5 dataset "name": shape (), type "|S12">
          test stepper
        /stepper/port
          <HDF5 dataset "channels": shape (4,), type "<i4">
            [1 2 3 4]
          <HDF5 dataset "device": shape (), type "|S12">
            /dev/comedi0
          <HDF5 dataset "direction": shape (), type "|S6">
            output
          <HDF5 dataset "name": shape (), type "|S12">
            stepper port
          <HDF5 dataset "subdevice": shape (), type "<i4">
            2
          <HDF5 dataset "subdevice-type": shape (), type "|S3">
            dio
        <HDF5 dataset "step-size": shape (), type "<f8">
          1.7e-07
      /temperature
        <HDF5 dataset "baudrate": shape (), type "<i4">
          9600
        <HDF5 dataset "controller": shape (), type "<i4">
          1
        <HDF5 dataset "device": shape (), type "|S10">
          /dev/ttyS0
        <HDF5 dataset "max-current": shape (), type "<f8">
          0.0
        <HDF5 dataset "name": shape (), type "|S16">
          test temperature
        <HDF5 dataset "units": shape (), type "|S7">
          Celsius
    >>> afm2 = pyafm.storage.load_afm(filename=filename)
    >>> afm2.load_from_config(devices=devices)

    >>> afm2.get_temperature()  # doctest: +SKIP
    297.37

    It's hard to test anything else without pugging into an actual AFM.

    >>> for device in devices:
    ...     device.close()

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    def __init__(self, config, piezo=None, stepper=None, temperature=None):
        self.config = config
        self.piezo = piezo
        self.stepper = stepper
        self.temperature = temperature

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if self.piezo is None and c['piezo']:
            self.piezo = _AFMPiezo(config=c['piezo'])
            self.piezo.load_from_config(devices=devices)
        if self.stepper is None and c['stepper']:
            self.stepper = _Stepper(config=c['stepper'])
            self.stepper.load_from_config(devices=devices)
        if self.temperature is None and c['temperature']:
            self.temperature = _Temperature(config=c['temperature'])
            self.temperature.load_from_config()

    def setup_config(self):
        if self.piezo:
            self.piezo.setup_config()
            self.config['piezo'] = self.piezo.config
        else:
            self.config['piezo'] = None
        if self.stepper:
            self.stepper.setup_config()
            self.config['stepper'] = self.stepper.config
        else:
            self.config['stepper'] = None
        if self.temperature:
            self.temperature.setup_config()
            self.config['temperature'] = self.temperature.config
        else:
            self.config['temperature'] = None

    def get_temperature(self):
        """Measure the sample temperature.

        Return the sample temperature in Kelvin or `None` if such a
        measurement is not possible.
        """
        if hasattr(self.temperature, 'get_temperature'):
            return self.temperature.get_temperature()
        return self.config['default-temperature']

    def move_just_onto_surface(self, depth=-50e-9, setpoint=2,
                               min_slope_ratio=10, far=200, steps=20,
                               sleep=0.0001):
        """Position the AFM tip close to the surface.

        Uses `.piezo.get_surface_position()` to pinpoint the position
        of the surface.  Adjusts the stepper position as required via
        `.stepper.single_step()` to get within
        `2*.stepper.step_size` meters of the surface.  Then adjusts
        the piezo to place the cantilever `depth` meters onto the
        surface.  Negative `depth`\s place the tip off the surface

        If `.piezo.get_surface_position()` fails to find the surface,
        backs off `far` half steps (for safety) and steps in (without
        moving the zpiezo) until deflection voltage is greater than
        `setpoint`.
        """
        _LOG.info('moving to %g onto the surface' % depth)

        stepper_tolerance = 2*self.stepper.step_size

        axis = self.piezo.axis_by_name(self.config['main-axis'])
        def_config = self.piezo.config.select_config('inputs', 'deflection')

        zero = _convert_volts_to_bits(axis.config['channel'], 0)
        target_def = _convert_volts_to_bits(def_config, setpoint)
        self._check_target_deflection(deflection=target_def)

        _LOG.debug('zero the %s piezo output' % self.config['main-axis'])
        self.piezo.jump(
            axis_name=self.config['main-axis'], position=zero, steps=steps,
            sleep=sleep)

        _LOG.debug("see if we're starting near the surface")
        try:
            pos = self.piezo.get_surface_position(
                axis_name=self.config['main-axis'], max_deflection=target_def,
                min_slope_ratio=min_slope_ratio)
        except _FlatFit, e:
            _LOG.info(e)
            pos = self._stepper_approach_again(
                target_deflection=target_def, min_slope_ratio=min_slope_ratio,
                far=far)
        except _SurfaceError, e:
            _LOG.info(e)
            pos = self._stepper_approach_again(
                target_deflection=target_def, min_slope_ratio=min_slope_ratio,
                far=far)

        pos_m = _convert_bits_to_meters(axis.config, pos)
        _LOG.debug('located surface at stepper %d, piezo %d (%g m)'
                  % (self.stepper.position, pos, pos_m))

        _LOG.debug('fine tune the stepper position')
        while pos_m < -stepper_tolerance:  # step back if we need to
            self.stepper.single_step(-1)
            _LOG.debug('step back to {}'.format(self.stepper.position))
            try:
                pos = self.piezo.get_surface_position(
                    axis_name=self.config['main-axis'],
                    max_deflection=target_def,
                    min_slope_ratio=min_slope_ratio)
            except _FlatFit, e:
                _LOG.debug(e)
                continue
            pos_m = _convert_bits_to_meters(axis.config, pos)
            _LOG.debug('located surface at stepper %d, piezo %d (%g m)'
                      % (self.stepper.position, pos, pos_m))
        while pos_m > stepper_tolerance:  # step forward if we need to
            self.stepper.single_step(1)
            _LOG.debug('step forward to {}'.format(self.stepper.position))
            try:
                pos = self.piezo.get_surface_position(
                    axis_name=self.config['main-axis'],
                    max_deflection=target_def,
                    min_slope_ratio=min_slope_ratio)
            except _FlatFit, e:
                _LOG.debug(e)
                continue
            pos_m = _convert_bits_to_meters(axis.config, pos)
            _LOG.debug('located surface at stepper %d, piezo %d (%g m)'
                      % (self.stepper.position, pos, pos_m))

        _LOG.debug('adjust the %s piezo to place us just onto the surface'
                  % self.config['main-axis'])
        target_m = pos_m + depth
        target = _convert_meters_to_bits(axis.config, target_m)
        self.piezo.jump(
            self.config['main-axis'], target, steps=steps, sleep=sleep)

        _LOG.debug(
            'positioned %g m into the surface at stepper %d, piezo %d (%g m)'
            % (depth, self.stepper.position, target, target_m))

    def _check_target_deflection(self, deflection):
        defc = self.piezo._deflection_channel()
        max_def = defc.get_maxdata()
        if deflection > max_def:
            _LOG.error(('requested setpoint ({} bits) is larger than the '
                        'maximum deflection value of {} bits'
                        ).format(deflection, max_def))
            raise ValueError(deflection)
        elif deflection < 0:
            _LOG.error(('requested setpoint ({} bits) is less than the '
                        'minimum deflection value of 0 bits'
                        ).format(deflection))
            raise ValueError(deflection)

    def _stepper_approach_again(self, target_deflection, min_slope_ratio, far):
        _LOG.info('back off %d half steps and approach until deflection > %g'
                 % (far, target_deflection))
        # back away
        self.stepper.step_relative(-far, backlash_safe=True)
        self.stepper_approach(target_deflection=target_deflection)
        for i in range(2*max(1, self.stepper.backlash)):
            _LOG.debug(
                'additional surface location attempt (stepping backwards)')
            try:
                pos = self.piezo.get_surface_position(
                    axis_name=self.config['main-axis'],
                    max_deflection=target_deflection,
                    min_slope_ratio=min_slope_ratio)
                return pos
            except _SurfaceError, e:
                _LOG.info(e)
            self.stepper.single_step(-1)  # step out
            _LOG.debug('stepped back to {}'.format(self.stepper.position))
        _LOG.debug('giving up on finding the surface')
        _LOG.warn(e)
        raise e

    def stepper_approach(self, target_deflection, record_data=None):
        _LOG.info('approach with stepper until deflection > {}'.format(
                target_deflection))
        if record_data is None:
            record_data = _package_config['matplotlib']
        if record_data:
            position = []
            deflection = []
        self._check_target_deflection(deflection=target_deflection)
        cd = self.piezo.read_deflection()  # cd = current deflection in bits
        _LOG.debug('single stepping approach')
        while cd < target_deflection:
            _LOG.debug('deflection {} < setpoint {}.  step closer'.format(
                    cd, target_deflection))
            self.stepper.single_step(1)  # step in
            cd = self.piezo.read_deflection()
            if record_data:
                position.append(self.stepper.position)
                deflection.append(cd)
        if _package_config['matplotlib']:
            figure = _matplotlib_pyplot.figure()
            axes = figure.add_subplot(1, 1, 1)
            axes.hold(False)
            timestamp = _time.strftime('%H-%M-%S')
            axes.set_title('stepper approach {}'.format(timestamp))
            plot = axes.plot(position, deflection, 'b.-')
            figure.canvas.draw()
            if hasattr(figure, 'show'):
                figure.show()
            if not _matplotlib.is_interactive():
                _matplotlib_pyplot.show()
        if record_data:
            return (position, deflection)

    def move_toward_surface(self, distance):
        """Step in approximately `distance` meters.
        """
        steps = int(distance/self.stepper.step_size)
        _LOG.info('step in {} steps (~{} m)'.format(steps, distance))
        self.stepper.step_relative(steps)

    def move_away_from_surface(self, distance=None):
        """Step back approximately `distance` meters.
        """
        if distance is None:
            distance = self.config['far']
        self.move_toward_surface(-distance)
