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

import os.path as _os_path

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage

from . import LOG as _LOG
from .afm import AFM as AFM
from .config import AFMConfig as _AFMConfig


DEFAULT_FILENAME = _os_path.expanduser(_os_path.join(
        '~', '.config', 'pyafm-default.h5'))
DEFAULT_GROUP = '/'


def save_afm(afm, filename=None, group=None):
    if filename is None:
        filename = DEFAULT_FILENAME
    if group is None:
        group = DEFAULT_GROUP
    assert group.endswith('/'), group
    _LOG.info('saving AFM config to {} {}'.format(filename, group))
    storage = _HDF5_Storage(filename=filename, group=group)
    storage.save(config=afm.config)

def load_config(filename=None, group=None):
    if filename is None:
        filename = DEFAULT_FILENAME
    if group is None:
        group = DEFAULT_GROUP
    assert group.endswith('/'), group
    _LOG.info('loading AFM config from {} {}'.format(filename, group))
    config = _AFMConfig(storage=_HDF5_Storage(filename=filename, group=group))
    config.load()
    return config

def load_afm(filename=None, group=None):
    config = load_config(filename=filename, group=group)
    _LOG.debug(
        'constructing AFM from configuration:\n{}'.format(config.dump()))
    return AFM(config=config)
