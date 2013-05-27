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

"""Define some variables to configure the package for a particular lab
and workflow."""

import os.path as _os_path
import sys as _sys

import h5config.config as _config
import h5config.tools as _h5config_tools
import numpy as _numpy
import pyafm.config as _pyafm_config


class PackageConfig (_h5config_tools.PackageConfig):
    "Configure `unfold_protein` module operation"
    settings = _h5config_tools.PackageConfig.settings + [
        _config.BooleanSetting(
            name='matplotlib',
            help='Plot piezo motion using `matplotlib`.',
            default=False),
        ]

class ApproachConfig (_config.Config):
    "Configure `unfold_protein` approach operation"
    settings = [
        _config.FloatSetting(
            name='relative setpoint',
            help=('Maximum relative deflection in volts to achieve the bind '
                  'position.'),
            default=2.0),
        _config.FloatSetting(
            name='velocity',
            help='Approach velocity in meters/second.',
            default=1e-6),
        _config.FloatSetting(
            name='step',
            help='Step size in meters.',
            default=5e-9),
        _config.IntegerSetting(
            name='far',
            help=('Approximate distance in meters to move away to get "far" '
                  'from the surface.  For possible stepper adjustments while '
                  'initially locating the surface.'),
            default=3e-5),
        ]

class UnfoldConfig (_config.Config):
    "Configure `unfold_protein` unfold operation"
    settings = [
        _config.FloatSetting(
            name='distance',
            help='Unfolding distance in meters.',
            default=800e-9),
        _config.FloatSetting(
            name='velocity',
            help='Unfolding velocity in meters/second.',
            default=1e-6),
        _config.FloatSetting(
            name='frequency',
            help='Sampling frequency in Hz.',
            default=50e3),
        ]

class SaveConfig (_config.Config):
    "Configure `unfold_protein` unfold operation"
    settings = [
        _config.Setting(
            name='base directory',
            help='Root directory for saving data.',
            default=_os_path.expanduser('~/rsrch/data/unfold/')),
        ]

class UnfoldCycleConfig (_config.Config):
    "Configure a full `unfold_protein` approach-bind-unfold cycle"
    settings = [
        _config.ConfigSetting(
            name='approach',
            help=('Configure the approach for an approach-bind-unfold '
                  'sequence.'),
            config_class=ApproachConfig),
        _config.FloatSetting(
            name='bind time',
            help=('Binding time in seconds for an approach-bind-unfold '
                  'sequence.'),
            default=3),
        _config.ConfigSetting(
            name='unfold',
            help=('Configure the unfolding for an approach-bind-unfold '
                  'sequence.'),
            config_class=UnfoldConfig),
        _config.ConfigSetting(
            name='save',
            help='Configure saving.',
            config_class=SaveConfig),
        _config.ConfigSetting(
            name='afm',
            help='Configure the AFM used for the unfolding experiments.',
            config_class=_pyafm_config.AFMConfig),
        ]

class VelocityScanConfig (_config.Config):
    "Configure `unfold_config` unfolding velocity scan"
    settings = [
        _config.FloatListSetting(
            name='unfolding velocities',
            help='Unfolding velocities in meters per second.',
            default=list(float(x) for x in _numpy.exp(_numpy.linspace(
                _numpy.log(20e-9), _numpy.log(2e-6), 10)))),
        _config.IntegerSetting(
            name='num loops',
            help='Number of loops through the scanned velocities.',
            default=10),
        ]

class PositionScanConfig (_config.Config):
    "Configure `unfold_config` contact position scan"
    settings = [
        _config.FloatSetting(
            name='x step',
            help=('Distance in meters along the x axis between successive '
                  'onfoldings.'),
            default=5e-9),
        _config.FloatSetting(
            name='x max',
            help='Maximum sampled x position in meters.',
            default=1e-6),
        _config.FloatSetting(
            name='x min',
            help='Minimum sampled x position in meters.',
            default=-1e-6),
        ]

class ScanConfig (_config.Config):
    "Configure a series of `unfold_protein` unfolding cycles"
    settings = [
        _config.ConfigSetting(
            name='velocity',
            help='Configure unfolding velocity scan pattern.',
            config_class=VelocityScanConfig),
        _config.ConfigSetting(
            name='position',
            help='Configure unfolding position scan pattern.',
            config_class=PositionScanConfig),
        _config.ConfigSetting(
            name='unfold',
            help='Configure a single approach-bind-unfold cycle.',
            config_class=UnfoldCycleConfig),
        ]
