# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

__metaclass__ = type

from cStringIO import StringIO
import logging, logging.handlers
import re
import sys
from time import sleep
import unittest

try:
    # Having PIL installed is nice for some test details but it is
    # not really urgent.
    import Image
    import ExifTags
except ImportError:
    Image = None

from devicecontroller import (
    LuaError,
    logger,
    PTPController,
    PTPControllerError,
    RPCMethod,
    ShootAction,
    split_lua_table_string,
    StuckMessage,
    )
from ptp import (
    CHDKScriptStatus,
    list_devices,
    PTPDevice
    )

def run_script(device, lua):
    """Run a script on the script and return its result.

    This function assumes that the script sends only its return message,
    no other should be sent to the host via usb_write_msg().
    """
    script_id = device.chdkExecLua(lua)
    while device.chdkScriptStatus(script_id) & CHDKScriptStatus.MSG == 0:
        sleep(0.1)
    msg_id = None
    while msg_id != script_id:
        msg, msg_type, msg_id = device.chdkReadScriptMessage()
    return msg


class BaseTestPTPDeviceController:

    def setUp(self):
        self.regular_handlers = logger.handlers[:]
        self.log_handler = logging.handlers.BufferingHandler(20)
        logger.addHandler(self.log_handler)
        # silence the regular logger handlers during tests; they
        # clutter the test output.
        # XXX this should be optional!
        for handler in self.regular_handlers:
            logger.removeHandler(handler)

    def tearDown(self):
        logger.removeHandler(self.log_handler)
        for handler in self.regular_handlers:
            logger.addHandler(handler)

    def makeController(self):
        controller = PTPController(self.device_info[0], self.device_info[1])
        device = controller.device
        script_id = controller.script_id
        return controller, device, script_id

    def test_create_instance(self):
        # When a PTPController is created, a script is running on the camera.
        controller, device, script_id = self.makeController()
        self.assertEqual(
            CHDKScriptStatus.RUN, device.chdkScriptStatus(script_id))
        del controller
        # Avoid spurious failures: wait a bit to ensure that all messages
        # are sent and processed.
        sleep(0.1)
        self.assertEqual(
            0, device.chdkScriptStatus(script_id))

    def test_stuck_message(self):
        # If a message is pending in the camera, it is consumed when
        # the PTPController instance is destroyed.
        controller, device, script_id = self.makeController()
        controller.rpcTest('send_message', 'foo')
        # wait a bit to let the camera execute the function.
        sleep(0.2)
        # The message is now waiting to be read by the host.
        self.assertEqual(
            CHDKScriptStatus.MSG,
            device.chdkScriptStatus(script_id) & CHDKScriptStatus.MSG)
        # When the controller is deleted, the destructor reads the pending
        # message and records an info level message.
        del controller
        self.assertEqual(1, len(self.log_handler.buffer))
        self.assertTrue(
            self.log_handler.buffer[0].getMessage().startswith(
                "Drained message: ('foo', 3,"))

    def test_echo(self):
        # Trivial form of regular host/camera communication: The host
        # sends a request, and the camera responds with a message.
        controller, device, script_id = self.makeController()
        result = controller.rpcTest('echo', 'foo')
        self.assertEqual('foo', result)

    def test_camera_runtime_error(self):
        # When a Lua error occurs during an RPC call, a LuaError is
        # raised on the host and the script started again.
        controller, device, script_id = self.makeController()
        with self.assertRaises(LuaError) as mgr:
            controller.rpcTest('runtime_error', 'bar_baz')
        message = str(mgr.exception)
        self.assertTrue(message.startswith(
            'Camera script error:\nruntime error:'))
        self.assertTrue('bar_baz' in message)
        self.assertEqual(script_id + 1, controller.script_id)
        self.assertEqual(
            CHDKScriptStatus.RUN, device.chdkScriptStatus(script_id))

    def test_lastImageFile(self):
        # Test of PTPController.lastImageFile().
        #
        # Defined in this class, not in FunctionalTestPTPDeviceController,
        # because it's a good idea to read the current file data
        # independently via helper scripts. In order to do this,
        # we use a simple PTPDevice instance, which would not work if we
        # have a PTPController connected to the camera at the same time.
        device = PTPDevice(self.device_info[0], self.device_info[1])
        dir_list = run_script(device, "return os.listdir('A/DCIM')")
        dir_list = [entry[1] for entry in split_lua_table_string(dir_list)
                    if re.search(r'^\d\d\d', entry[1])]
        if not dir_list:
            print >>sys.stderr, "No image directory found, test aborted."
            return
        last_dir = 'A/DCIM/%s' % sorted(dir_list)[-1]
        file_list = run_script(device, "return os.listdir('%s')" % last_dir)
        # We can get an out of memory error here
        if file_list.startswith('runtime error'):
            print >>sys.stderr, (
                "Can't retrieve file list from camera: %s" % file_list)
            print >>sys.stderr, "Incomplete test."
            file_list = None
        else:
            file_list = [entry[1] for entry in split_lua_table_string(file_list)
                         if re.search(r'^....\d\d\d\d\....$', entry[1])]
            if len(file_list) == 0:
                print >>sys.stderr, "Empty image directory, test aborted."
                return
            last_file = sorted(file_list)[-1]
        del device
        ctrl = PTPController(self.device_info[0], self.device_info[1])
        if file_list is not None:
            self.assertEqual(
                '%s/%s' % (last_dir, last_file), ctrl.lastImageName())

    def test_recentImages(self):
        # recentImages() returns a sequence of image files paths.
        result = list(PTPController.recentImages(
            'A/DCIM/123CANON/IMG_3456.JPG', 'A/DCIM/123CANON/IMG_3458.JPG'))
        expected = [
            'A/DCIM/123CANON/IMG_3457.JPG', 'A/DCIM/123CANON/IMG_3458.JPG']
        self.assertEqual(expected, result)
        result = list(PTPController.recentImages(
            'A/DCIM/123CANON/MOV_9998.JPG', 'A/DCIM/124CANON/IMG_0001.JPG'))
        expected = [
            'A/DCIM/123CANON/IMG_9999.JPG', 'A/DCIM/124CANON/IMG_0001.JPG']
        self.assertEqual(expected, result)



class FunctionalTestPTPDeviceController:

    def setUp(self):
        super(FunctionalTestPTPDeviceController, self).setUp()
        self.ctrl = PTPController(
            bus=self.device_info[0], device=self.device_info[1])

    def tearDown(self):
        del self.ctrl
        super(FunctionalTestPTPDeviceController, self).tearDown()

    def test_set_get_mode(self):
        # We can set and check the camera mode (record/playback).
        recording, video, mode_num = self.ctrl.setMode(1)
        self.assertTrue(recording)
        self.assertFalse(video)
        # The exact mode number depends on the setting of the camera's
        # mode wheel and the camera model.
        self.assertIs(int, type(mode_num))
        recording, video, mode_num = self.ctrl.getMode()
        self.assertTrue(recording)
        self.assertFalse(video)
        self.assertIs(int, type(mode_num))

        recording, video, mode_num = self.ctrl.setMode(0)
        self.assertFalse(recording)
        self.assertFalse(video)
        self.assertIs(int, type(mode_num))
        recording, video, mode_num = self.ctrl.getMode()
        self.assertFalse(recording)
        self.assertFalse(video)
        self.assertIs(int, type(mode_num))

    # XXX a quite well reproducible timeout error is raised in test_shoot()
    # and test_shootHalf() when these tests are run with the SX30 and
    # its lens covered by a cap.
    # This error makes the camera unresponsive after two or three runs.
    def test_shootHalf(self):
        self.ctrl.setMode(1)

        # shootHalf() can return immediately; at this time, the camera
        # is not yet ready to take a photo.
        self.ctrl.shootHalf(enable=True, wait_until_ready=False)
        self.assertFalse(self.ctrl.getShooting())
        sleep(1)
        self.ctrl.shootHalf(enable=False)

        # Alternatively, shootHalf() can wait until the camera is ready
        # to take a photo.
        self.ctrl.shootHalf(enable=True, wait_until_ready=True)
        self.assertTrue(self.ctrl.getShooting())
        self.ctrl.shootHalf(enable=False)

        self.ctrl.setMode(0)

        # We get an error when shootHalf() is called in playback mode.
        with self.assertRaises(PTPControllerError) as mgr:
            self.ctrl.shootHalf(True)
        self.assertEqual('not in recording mode', mgr.exception.message)

    def test_shoot(self):
        self.ctrl.setMode(1)

        # We can issue a short "click", resulting in one new image.
        count_1 = self.ctrl.exposureCount()
        self.ctrl.shoot(ShootAction.CLICK_BUTTON)
        count_2 = self.ctrl.exposureCount()
        # XXX This assertion fails sometimes, with
        # (count_2 - count_1) % 9999 having a value of 2 or larger...
        self.assertEqual(1, (count_2 - count_1) % 9999)
        # We can keep the "shoot_full" button pressed. Depending on the
        # camera settings, this can result in more than one new image.
        self.ctrl.shoot(ShootAction.PRESS_BUTTON)
        sleep(2)
        self.ctrl.shoot(ShootAction.RELEASE_BUTTON)
        count_3 = self.ctrl.exposureCount()
        self.assertTrue((count_3 - count_2) % 9999 >= 1)

        self.ctrl.setMode(0)

        # We get an error when shoot() is called in playback mode.
        with self.assertRaises(PTPControllerError) as mgr:
            self.ctrl.shoot(ShootAction.CLICK_BUTTON)
        self.assertEqual('not in recording mode', mgr.exception.message)

    def test_stuck_message(self):
        # When an RPCMethod times out, a subsequent call of any
        # RPCMethod raises a StuckMessage error, until the pending message
        # is received.

        # First, we get a timeout error.
        with self.assertRaises(PTPControllerError):
            self.ctrl.rpcTest('timeout', 1)

        # For the next second, no message will be available from the
        # camera, and we get a StuckMessage back, where
        # exc.message[0] is False.
        with self.assertRaises(StuckMessage) as mgr:
            self.ctrl.rpcTest('echo', 'foo')
        self.assertFalse(mgr.exception.message[0])
        self.assertIs(None, mgr.exception.message[1])

        # After waiting for another second (plus slack time for the camera)
        # a message will be available, but the RPCMethod call will still
        # fail.
        sleep(1.1)
        with self.assertRaises(StuckMessage) as mgr:
            self.ctrl.rpcTest('echo', 'foo')
        self.assertTrue(mgr.exception.message[0])
        self.assertEqual('ready', mgr.exception.message[1])

        # The next call of the RPC method will succeed.
        self.assertEqual('foo', self.ctrl.rpcTest('echo', 'foo'))

    def test_zoom(self):
        if 'SX100' in self.ctrl.device.model:
            self.skipTest(
                'setZoom is known to crash the %s' % self.ctrl.device.model)
        zoom_steps = self.ctrl.zoomSteps()
        self.ctrl.setMode(1)
        self.ctrl.setZoom(0)
        self.assertEqual(0, self.ctrl.getZoom())
        half_zoom = zoom_steps / 2
        self.ctrl.setZoom(half_zoom)
        self.assertEqual(half_zoom, self.ctrl.getZoom())
        self.ctrl.setZoom(zoom_steps)
        self.assertEqual(zoom_steps - 1, self.ctrl.getZoom())
        self.ctrl.setZoom(0)
        self.assertEqual(0, self.ctrl.getZoom())

        self.ctrl.setMode(0)

        # ensure that list_devices() below can open a session.
        self.ctrl = None
        if self.device_info[4] == 'Canon PowerShot SX40 HS':
            # Check that the SX40 does not pwer off with a lens error.
            # This happens typically 8 or 9 seconds after the setZoom()
            # call.
            print self.device_info
            for x in range(12):
                sleep(1)
                devices = list_devices()
                if self.device_info not in devices:
                    self.fail('Camera powered off after setZoom()')

    def test_supportedCaptureModes(self):
        result = self.ctrl.supportedCaptureModes()
        # The exact content of result depends of course on the camera model;
        # it should be safe to assume that at least the modes "AUTO" and "P"
        # are always supported.
        self.assertEqual(1, result['AUTO'])
        self.assertEqual(2, result['P'])

    def test_setCaptureMode(self):
        self.ctrl.setMode(1)
        modes = self.ctrl.supportedCaptureModes()
        for name in modes:
            self.assertTrue(self.ctrl.setCaptureMode(name))
            recording, video, mode = self.ctrl.getMode()
            self.assertEqual(modes[name], mode & 0xFF)

        # Note that changing the capture mode does not work when the
        # camera is in playback.
        self.ctrl.setCaptureMode('P')
        self.ctrl.setMode(0)
        self.assertFalse(self.ctrl.setCaptureMode('AUTO'))
        recording, video, mode = self.ctrl.getMode()
        self.assertEqual(modes['P'], mode & 0xFF)

    def test_get_setISO(self):
        # Each camera should support a number of ISO modes, where the
        # mode numbers begin with 0. An attempt to set an unsupported
        # mode fails with PTPControllerError.
        iso_mode = 0
        while True:
            try:
                result = self.ctrl.setISO(iso_mode)
            except PTPControllerError:
                break
            self.assertEqual(result, iso_mode)
            iso_mode += 1

        # We should have at least the auto ISO mode and a few manual
        # ISO settings.
        self.assertTrue(iso_mode >= 2)

    @unittest.skipIf(Image is None,
                     "This test reqires the Python Imaging Library.")
    def test_setISO_image_check(self):
        # Check if a chosen ISO mode also appears in the EXIF data of
        # an image.
        exif_iso_num = None
        for k, v in ExifTags.TAGS.items():
            if v == 'ISOSpeedRatings':
                exif_iso_num = k
                break
        if exif_iso_num is None:
            print >>sys.stderr, (
                "Warning: Could not determine the EXIF speed index.")
            return
        self.ctrl.setMode(1)
        self.ctrl.setCaptureMode('P')
        # The ISO mode 1 (80 for the A810, SX100, SX30) seems to be
        # a bit of cheating: The EXIF data for pictures taken with this
        # setting say that ISO 100 was used. So let's use a value that
        # should be 100 ISO on most cameras.
        ISO_MODE_100 = 2
        self.ctrl.setISO(ISO_MODE_100)
        self.ctrl.shoot()
        filename = self.ctrl.lastImageName()
        im = self.ctrl.device.chdkDownloadString(filename)
        im = Image.open(StringIO(im))
        im.load()
        recorded_iso = im._getexif()[exif_iso_num]
        self.assertEqual(recorded_iso, self.ctrl.iso_map[ISO_MODE_100])

        max_iso_index = max(self.ctrl.iso_map)
        self.ctrl.setISO(max_iso_index)
        self.ctrl.shoot()
        filename = self.ctrl.lastImageName()
        im = self.ctrl.device.chdkDownloadString(filename)
        im = Image.open(StringIO(im))
        im.load()
        recorded_iso = im._getexif()[exif_iso_num]
        self.assertEqual(recorded_iso, self.ctrl.iso_map[max_iso_index])

        self.ctrl.setMode(0)

    def test_getFocus(self):
        self.ctrl.setMode(1)
        info = self.ctrl.getFocus()
        self.assertTrue(isinstance(info[0], int))
        self.assertTrue(isinstance(info[1], int))
        self.assertTrue(isinstance(info[2], bool))
        # Without shootHalf pressed, focus_state should be "not focussed"
        self.assertEqual(0, info[0])
        # and the camera is not ready for shooting.
        self.assertFalse(info[2])
        # Pressing "shoot half" should give a focussed image after
        # a few seconds.
        self.ctrl.shootHalf(True)
        for i in range(50):
            sleep(0.1)
            info = self.ctrl.getFocus()
            if info[2]:
                break
        self.assertTrue(info[2])
        self.assertTrue(info[0] > 0)
        self.ctrl.shootHalf(False)
        self.ctrl.setMode(0)


module = sys.modules[__name__]
all_devices = list_devices()
if not all_devices:
    print >>sys.stderr, "No devices found"
for info in all_devices:
    device_name = info[4].replace(' ', '_')

    for test_case in (BaseTestPTPDeviceController,
                      FunctionalTestPTPDeviceController):
        testname = '%s_%s_%s_%s' % (
            test_case.__name__, device_name, info[0], info[1])
        module.__dict__[testname] = type(
            testname, (test_case, unittest.TestCase), {'device_info': info})
