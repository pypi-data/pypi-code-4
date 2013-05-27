# Copyright

import os.path as _os_path

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
from h5config.storage.yaml import YAML_Storage as _YAML_Storage
import pyafm.storage as _pyafm_storage

from . import LOG as _LOG
from . import config as _config
from . import scan as _scan


DEFAULT_FILENAME = _os_path.expanduser(_os_path.join(
        '~', '.config', 'unfold-default.yaml'))
DEFAULT_GROUP = '/'


def _get_storage(filename=None, group=None, action=None):
    if filename is None:
        filename = DEFAULT_FILENAME
    if filename.endswith('.h5'):
        if group is None:
            group = DEFAULT_GROUP
        assert group.endswith('/'), group
        _LOG.info('{} {} {}'.format(action, filename, group))
        storage = _HDF5_Storage(filename=filename, group=group)
    elif filename.endswith('.yaml'):
        assert group is None, group
        _LOG.info('{} {}'.format(action, filename))
        storage = _YAML_Storage(filename=filename)
    else:
        raise ValueError('unrecognized file extension in {}'.format(filename))
    return storage


def save_scan_config(config, filename=None, group=None):
    storage = _get_storage(
        filename=filename, group=group,
        action='saving unfolding scan config to')
    storage.save(config=config)


def load_scan_config(filename=None, group=None):
    storage = _get_storage(
        filename=filename, group=group,
        action='loading unfolding scan config from')
    config = _config.ScanConfig(storage=storage)
    config.load()
    return config


def load_scanner(filename=None, group=None):
    config = load_scan_config(filename=group, group=group)
    _LOG.debug(
        'constructing UnfoldScanner from configuration:\n{}'.format(
            config.dump()))
    scanner = _scan.UnfoldScanner(config=config)
    return scanner


def get_default_config():
    scan_config = _config.ScanConfig()
    scan_config['velocity'] = _config.VelocityScanConfig()
    scan_config['position'] = _config.PositionScanConfig()
    scan_config['unfold'] = _config.UnfoldCycleConfig()
    scan_config['unfold']['approach'] = _config.ApproachConfig()
    scan_config['unfold']['unfold'] = _config.UnfoldConfig()
    scan_config['unfold']['save'] = _config.SaveConfig()
    scan_config['unfold']['afm'] = _pyafm_storage.load_config()
    return scan_config
