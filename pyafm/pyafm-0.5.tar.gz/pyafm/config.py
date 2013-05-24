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

"AFM configuration"

import h5config.config as _config
import h5config.tools as _h5config_tools
import pycomedi.constant as _constant
import pypiezo.config as _pypiezo_config


class PackageConfig (_h5config_tools.PackageConfig):
    "Configure `pyafm` module operation"
    settings = _h5config_tools.PackageConfig.settings + [
        _config.BooleanSetting(
            name='matplotlib',
            help='Plot pyafm actions using `matplotlib`.',
            default=False),
        ]


class _TemperatureUnit (object):
    pass


class Celsius (_TemperatureUnit):
    pass


class Kelvin (_TemperatureUnit):
    pass


class TemperatureConfig (_config.Config):
    "Configure a temperature monitor"
    settings = [
        _config.Setting(
            name='name',
            help='Monitor name (so the user will know what is measured).',
            default=None),
        _config.ChoiceSetting(
            name='units',
            help='Units of raw temperature measurements.',
            default=Celsius,
            choices=[
                ('Celsius', Celsius),
                ('Kelvin', Kelvin),
                ]),
        _config.IntegerSetting(
            name='controller',
            help='MTCA controller ID.',
            default=1),
        _config.Setting(
            name='device',
            help="Serial port you're using to connect to the controller.",
            default='/dev/ttyS0'),
        _config.IntegerSetting(
            name='baudrate',
            help="Baud rate for which you've configured your controller.",
            default=9600),
        _config.FloatSetting(
            name='max-current',
            help="Maxium current (in amps) output by the controller.",
            default=0),
        ]


class DigitalPortConfig (_config.Config):
    "Configure a digital input/output port."
    settings = [
        _config.Setting(
            name='name',
            help="Port name (so the user will know what it's used for).",
            default=None),
        _config.Setting(
            name='device',
            help='Comedi device.',
            default='/dev/comedi0'),
        _config.IntegerSetting(
            name='subdevice',
            help='Comedi subdevice index.  -1 for automatic detection.',
            default=-1),
        _config.ChoiceSetting(
            name='subdevice-type',
            help='Comedi subdevice type for autodetection.',
            choices=[(x.name, x) for x in _constant.SUBDEVICE_TYPE],
            default=_constant.SUBDEVICE_TYPE.dio),
        _config.IntegerListSetting(
            name='channels',
            help='Subdevice channels to control by index.',
            default=[0]),
        _config.ChoiceSetting(
            name='direction',
            help='Port direction.',
            choices=[(x.name, x) for x in _constant.IO_DIRECTION]),
        ]


class StepperConfig (_config.Config):
    "Configure a stepper motor."
    settings = [
        _config.Setting(
            name='name',
            help="Motor name (so the user will know what it's used for).",
            default=None),
        _config.BooleanSetting(
            name='full-step',
            help='Place the stepper in full-step mode (vs. half-step)',
            default=True),
        _config.BooleanSetting(
            name='logic',
            help='Place the stepper in active-high mode (vs. active-low)',
            default=True),
        _config.FloatSetting(
            name='delay',
            help=('Time delay between steps in seconds, in case the motor '
                  'response is slower that the digital output driver.'),
            default=1e-2),
        _config.FloatSetting(
            name='step-size',
            help= 'Approximate step size in meters.' ,
            default=170e-9),
        _config.IntegerSetting(
            name='backlash',
            help= 'Generous estimate of the backlash length in half-steps.',
            default=100),
        _config.ConfigSetting(
            name='port',
            help=('Configure the digital port used to communicate with the '
                  'stepper.'),
            config_class=DigitalPortConfig,
            default=None),
        ]


class AFMConfig (_config.Config):
    "Configure an Atomic Force Microscope (AFM)."
    settings = [
        _config.Setting(
            name='name',
            help="AFM name (so the user will know what it's used for).",
            default=None),
        _config.Setting(
            name='main-axis',
            help=("Name of the piezo axis controlling distance from the "
                  "surface."),
            default=None),
        _config.ConfigSetting(
            name='piezo',
            help='Configure the underlying piezo (fine adjustment).',
            config_class=_pypiezo_config.PiezoConfig,
            default=None),
        _config.ConfigSetting(
            name='stepper',
            help='Configure the underlying stepper motor (coarse adjustment).',
            config_class=StepperConfig,
            default=None),
        _config.ConfigSetting(
            name='temperature',
            help='Configure the underlying temperature sensor.',
            config_class=TemperatureConfig,
            default=None),
        _config.FloatSetting(
            name='fallback-temperature',
            help=('Temperature in Kelvin to use if no temperature sensor is '
                  'configured.'),
            default=295.15),
        _config.FloatSetting(
            name='far',
            help=('Approximate distance in meters to move away to get "far" '
                  'from the surface.  For possible stepper adjustments while '
                  'initially locating the surface.'),
            default=3e-5),
        ]
