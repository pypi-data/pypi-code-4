#!/usr/bin/env python

# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
from distutils.core import Extension, setup
from distutils.command.build_clib import build_clib as _build_clib
from distutils.command.build_ext import build_ext as _build_ext
from tools.ptp_h_parser import constants_from_header_file

_ptp_h_params = [
    ('Vendor', 'PTP_VENDOR_'),
    ('OperationCode', 'PTP_OC_'),
    ('ResponseCode', 'PTP_RC_'),
    ('PTPErrorID', 'PTP_ERROR_'),
    ('EventCode', 'PTP_EC_'),
    ('ObjectFormat', 'PTP_OFC_'),
    ('AssociationType', 'PTP_AT_'),
    ('ProtectionStatus', 'PTP_PS_'),
    ('StorageType', 'PTP_ST_'),
    ('FileSystemType', 'PTP_FST_'),
    ('AccessCapability', 'PTP_AC_'),
    ('PropertyID', 'PTP_DPC_'),
    ('CHDKScriptType', 'PTP_CHDK_SL_'),
    ('CHDKScriptStatus', 'PTP_CHDK_SCRIPT_STATUS_'),
    ('CHDKMessageType', 'PTP_CHDK_S_MSGTYPE_'),
    ('CHDKMessageStatus', 'PTP_CHDK_S_MSGSTATUS_'),
    ('LiveViewFlags', 'LV_TFR_')
]


class build_ext(_build_ext):
    def run(self):
        """We want to build the file src/pyptp-constants-data.c from
        src/ptp.h.

        Since this (as well as building the whole library) is very fast,
        don't bother at all for now about defining dependencies.
        """
        dest = open('src/pyptp-constants-data.c', 'w')
        constants_from_header_file(
            ('src/ptp.h', 'src/ptp-chdk.h',
             'src/chdk_headers/core/ptp.h',
             'src/chdk_headers/core/live_view.h'),
            dest, _ptp_h_params)
        dest.close()
        _build_ext.run(self)


ptp = Extension(
    'pyptpchdk',
    sources=['src/ptp.c', 'src/myusb.c', 'src/pyptp.c', 'src/ptp-chdk.c'],
    libraries=['usb'],
)

setup(
    name="pyptpchdk",
    version='0.2.1',
    description=(
        'A Picture Transfer Protocol module supporting CHDK extensions'),
    author='Abel Deuring',
    author_email='adeuring@gmx.net',
    license='GPL2',
    ext_modules=[ptp],
    py_modules=['devicecontroller'],
    package_dir={'': 'py'},
    cmdclass = {
        'build_ext': build_ext,
})
