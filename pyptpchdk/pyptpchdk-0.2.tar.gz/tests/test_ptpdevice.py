# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

from camera_info import connected_cameras, skipWithCamera, skipWithoutCamera
import ptp
import sys
from unittest import TestCase


class TestPTPDevice(TestCase):

    def setUp(self):
        self.device = ptp.PTPDevice

    @skipWithCamera()
    def test_createPTPDevive__without_camera(self):
        with self.assertRaises(ptp.PTPError) as checker:
            ptp.PTPDevice()
        self.assertEqual("Can't find a camera.", str(checker.exception))

    @skipWithoutCamera()
    def test_createPTPDevice__no_params(self):
        device = ptp.PTPDevice()
        # Should be listed in connected_cameras.
        found = False
        unknown_camera_connected = False
        for info in connected_cameras.values():
            if info.known_camera:
                if device.model == info.model:
                    found = True
                    break
            else:
                unknown_camera_connected = True
        if not found and not unknown_camera_connected:
            self.fail('Could not find camera in list of known models')

    @skipWithoutCamera()
    def test_createPTPDevice__with_params(self):
        all_cameras = ptp.list_devices()
        for bus_no, device_no, vendor_id, product_id, name in all_cameras:
            device = ptp.PTPDevice(bus_no, device_no)
            expected = connected_cameras[(bus_no, device_no)]
            if not expected.known_camera:
                print "Warning: Unknown camera. No full test possible."
                return

            for attr in (
                'functional_mode', 'model', 'standard_version', 'vendor'):
                result = getattr(device, attr)
                wanted = getattr(expected, attr)
                self.assertEqual(
                    wanted, result,
                    'bus: %03i device: %03i vendor %04x product %04x: '
                    'attribute %s does not match\n'
                    '  expected: %r\n'
                    '  got:      %r'
                    % (bus_no, device_no, vendor_id, product_id, attr,
                       wanted, result))
            for attr in (
                'capture_formats', 'image_formats',
                'supported_device_properties', 'supported_operations',
                ):
                # sequences. The data retrieved from the camera is not
                # necessarily sorted.
                result = sorted(getattr(device, attr))
                wanted = getattr(expected, attr)
                self.assertEqual(
                    wanted, result,
                    'bus: %03i device: %03i vendor %04x product %04x: '
                    'attribute %s does not match\n'
                    '  expected: %r\n'
                    '  got:      %r'
                    % (bus_no, device_no, vendor_id, product_id, attr,
                       wanted, result))
            for attr in (
                'serial_number', 'vendor_extension_description',
                'vendor_extension_id', 'vendor_extension_version', 'version'):
                # just ensure that we can access these attributes
                # xxx we should check the type of the properties.
                # This would be easy with an assertTaht method, where
                # we define matchers in the CameraInfo class.
                result = getattr(device, attr)
