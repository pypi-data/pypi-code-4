# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

from camera_info import connected_cameras
import ptp
from unittest import skip, TestCase

class TestModule(TestCase):
    """Misc tests."""

    def test_list_devices__arguments(self):
        # ptp.list_devices can be called without arguments.
        ptp.list_devices()
        # Or with one argument.
        ptp.list_devices(1)
        # Or one keyword argument.
        ptp.list_devices(force=0)
        # But not with the wrong parameter name.
        with self.assertRaises(TypeError):
            ptp.list_devices(foo=1)
        # Or with two parameters.
        with self.assertRaises(TypeError):
            ptp.list_devices(1, 2)

    def test_list_devices__default_result(self):
        devices = ptp.list_devices()
        for bus, device, vendor_id, product_id, name in devices:
            expected = connected_cameras[(bus, device)]
            self.assertEqual(expected.vendor_id, vendor_id)
            self.assertEqual(expected.product_id, product_id)
            if expected.known_camera:
                self.assertEqual(expected.model, name)
            else:
                print (
                    "\nWarning: testing for a camera that has no test "
                    "information: %s" % name)
                print "  USB vendor:product %04x:%04x" % (vendor_id, product_id)

        self.assertEqual(
            len(connected_cameras), len(devices),
            "Number of devices found by lsusb (%i) does not match number\n"
            "of devices found by ptp.list_devices() (%i).\n"
            "Also, note that gvfsd-gphoto2 may block access to a camera.\n"
            "You might consider to kill gvfsd-gphoto2 before running tests.."
            % (len(connected_cameras), len(devices)))
