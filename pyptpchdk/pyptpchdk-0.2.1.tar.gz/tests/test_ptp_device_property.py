# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

from camera_info import connected_cameras, skipWithoutCamera
import ptp
from testtools import skip, TestCase

class TestDeviceProperty(TestCase):

    @skip('XXX Confuses tests in test_devicecontroller.py. Exact reason '
          'unknown...')
    @skipWithoutCamera()
    def test_non_existent_property(self):
        device = ptp.PTPDevice()
        index = 0
        all_properties = device.supported_device_properties
        while index in all_properties:
            index += 1
        exc = self.assertRaises(ptp.PTPError, device.getDeviceProperty, index)
        self.assertIn(
            tuple(exc),
            # SX100, EOS400D, for example
            ((ptp.PTPErrorID.DATA_EXPECTED,
             'Unknown PTP call error: 2fe'),
             # SX30, for example
             (ptp.ResponseCode.ParameterNotSupported,
              'PTP error: Parameter not supported (2006).'),
            ))

    @skip('XXX Confuses tests in test_devicecontroller.py. Exact reason '
          'unknown...')
    @skipWithoutCamera()
    def test_properties(self):
        all_cameras = ptp.list_devices()
        for bus_no, device_no, vendor_id, product_id, name in all_cameras:
            device = ptp.PTPDevice(bus_no, device_no)
            expected = connected_cameras[(bus_no, device_no)]
            self.property_tests_for_camera(device, expected)

    def property_tests_for_camera(self, camera, expected):
        for prop_id in sorted(camera.supported_device_properties):
            self.assertThat(camera, expected.matchProperty(prop_id))
