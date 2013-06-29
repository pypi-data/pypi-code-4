# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

from datetime import datetime
import random
import tempfile
from testtools import TestCase
from testtools.content import text_content
from time import sleep, time

from camera_info import connected_cameras, skipWithoutCamera
import ptp

class TestDeviceOperations(TestCase):

    @skipWithoutCamera()
    def test_operations(self):
        all_cameras = ptp.list_devices()
        for bus_no, device_no, vendor_id, product_id, name in all_cameras:
            self.addDetail(
                'camera', text_content(u'%03i:%03i' % (bus_no, device_no)))
            device = ptp.PTPDevice(bus_no, device_no)
            expected = connected_cameras[(bus_no, device_no)]
            self.operation_tests_for_camera(device, expected)

    def operation_tests_for_camera(self, camera, expected):
        supported_by_camera = set(camera.supported_operations)
        existing_tests = set(self.optests.keys())
        for op in sorted(existing_tests.intersection(supported_by_camera)):
            self.optests[op](self, camera, expected)

    def storage_ids_test(self, camera, expected):
        storage_ids = camera.storage_ids
        self.assertIsInstance(storage_ids, tuple)
        for sid in storage_ids:
            self.assertIsInstance(sid, int)

    def storage_info_test(self, camera, expected):
        storage_ids = camera.storage_ids
        for sid in storage_ids:
            info = camera.getStorageInfo(sid)
            self.assertIsInstance(info, dict)
            required_keys = set((
                "storage_type", "file_system_type", "access_capability",
                "max_capability", "free_space_in_bytes",
                "free_space_in_images"))
            optional_keys = set(( "description", "volume_label"))
            device_keys = set(info.keys())
            self.assertTrue(device_keys.issuperset(required_keys))
            device_optional = device_keys.difference(required_keys)
            self.assertTrue(device_optional.issubset(optional_keys))
            for key in required_keys:
                self.assertIsInstance(info[key], int)
            for key in device_optional:
                self.assertIsInstance(info[key], str)

    def object_handles_test(self, camera, expected):
        for storage_id in camera.storage_ids:
            # xxx we shoudl also check the optional parameters!
            object_handles = camera.getObjectHandles(storage_id)
            self.assertIsInstance(object_handles, tuple)
            for oid in object_handles:
                self.assertIsInstance(oid, int)

    def object_info_test(self, camera, expected):
        for storage_id in camera.storage_ids:
            object_handles = camera.getObjectHandles(storage_id)
            for oid in object_handles:
                info = camera.getObjectInfo(oid)
                self.assertIsInstance(info, dict)
                optional_keys = set(("filename", "keywords"))
                required_keys = set((
                    "storage_id", "object_format", "protection_status",
                    "compressed_size", "thumb_format",
                    "thumb_compressed_size", "thumb_pix_width",
                    "thumb_pix_height", "image_pix_width", "image_pix_height",
                    "image_bit_depth", "parent_object", "association_type",
                    "association_desc", "sequence_number",
                    "capture_date", "modification_date"))
                device_keys = set(info.keys())
                self.assertTrue(required_keys.issubset(device_keys))
                device_optional = device_keys.difference(required_keys)
                self.assertTrue(device_optional.issubset(optional_keys))

                for k in ("storage_id", "object_format", "protection_status",
                          "compressed_size", "thumb_format",
                          "thumb_compressed_size", "thumb_pix_width",
                          "thumb_pix_height", "image_pix_width",
                          "image_pix_height", "image_bit_depth",
                          "parent_object", "association_type",
                          "association_desc", "sequence_number"):
                    self.assertIsInstance(info[k], int)
                for k in ("filename", "keywords"):
                    if k in device_keys:
                        self.assertIsInstance(info[k], str)
                for k in ("capture_date", "modification_date"):
                    self.assertIsInstance(info[k], datetime)

    def get_object_test(self, camera, expected):
        for h in camera.getObjectHandles(-1):
            # The cameras sometime refuse to return data for directory
            # objects.
            try:
                camera.getObject(h)
            except ptp.PTPError, err:
                if tuple(err) != (ptp.ResponseCode.InvalidObjectHandle,
                                  'PTP error: Invalid object handle(2009).'):
                    raise

    def chdk_test(self, camera, expected):
        if camera.chdkScriptSupport():
            self.chdk_script_test(camera, expected)
        # xxx Has the preview feature indeed been introduced with
        # version 2.4 of the CHDK PTP support? Or perhaps a bit earlier?
        if camera.chdkGetPTPVersion() >= (2, 4):
            self.chdk_preview_test(camera)
        self.chdk_upload_download_test(camera)

    def chdk_script_test(self, camera, expected):
        script_id = camera.chdkExecLua('return 1 + 1')
        while (camera.chdkScriptStatus(script_id) & ptp.CHDKScriptStatus.RUN):
            sleep(0.1)
        result, result_type, script_id_msg = camera.chdkReadScriptMessage()
        self.assertEqual(2, result)
        self.assertEqual(ptp.CHDKMessageType.RET, result_type)
        self.assertEqual(script_id, script_id_msg);
        # A script is basically a function: It must return something.
        # A script without a "return something" ends with an error.
        script_id = camera.chdkExecLua('1 + 1')
        while (camera.chdkScriptStatus(script_id) & ptp.CHDKScriptStatus.RUN):
            sleep(0.1)
        result, result_type, script_id_msg = camera.chdkReadScriptMessage()
        self.assertEqual(
            "syntax error: :1: unexpected symbol near '1'", result)
        self.assertEqual(ptp.CHDKMessageType.ERR, result_type)
        self.assertEqual(script_id, script_id_msg);

        # Send a message to a script and wait for an echo.
        script_id = camera.chdkExecLua('''
            msg = read_usb_msg(1)
            write_usb_msg(msg .. msg)
            -- wait a bit before terminating so that the host can read the
            -- message sent above. Otherwise, the message seems to be
            -- dropped.
            sleep(100)
            return 42
            ''')
        write_status = camera.chdkWriteScriptMessage('foo', script_id)
        self.assertEqual(ptp.CHDKMessageStatus.OK, write_status)
        wait_until = time() + 5
        status = camera.chdkScriptStatus(script_id)
        returned_message = None
        while status & ptp.CHDKScriptStatus.RUN and time() < wait_until:
            if status & ptp.CHDKScriptStatus.MSG:
                returned_message = camera.chdkReadScriptMessage()
            else:
                sleep(0.1)
            status = camera.chdkScriptStatus(script_id)

        status = camera.chdkScriptStatus(script_id)
        while (status & ptp.CHDKScriptStatus.RUN) and time() < wait_until:
            status = camera.chdkScriptStatus(script_id)
        if (status & ptp.CHDKScriptStatus.RUN):
            self.fail(
                'Script did not finish. This may affect subsequent tests, '
                'please power-cycle the camera.')
        if (status & ptp.CHDKScriptStatus.MSG):
            script_result = camera.chdkReadScriptMessage()
        self.assertEqual(
            ('foofoo', ptp.CHDKMessageType.USER, script_id) , returned_message)
        self.assertEqual(
            (42, ptp.CHDKMessageType.RET, script_id), script_result)

    def chdk_preview_test(self, camera):
        result = camera.chdkGetLiveData(ptp.LiveViewFlags.BITMAP)
        self.assertEqual(
            set(('lcd_aspect_ratio', 'version_major', 'version_minor',
                 'bitmap')),
            set(result.keys()))
        bitmap = result['bitmap']
        self.assertEqual(
            set(('width', 'height', 'data')), set(bitmap.keys()))
        # The bitmap data is a string with RGBA data, i.e., four bytes
        # per pixel.
        self.assertEqual(
            bitmap['width'] * bitmap['height'] * 4, len(bitmap['data']))

        result = camera.chdkGetLiveData(ptp.LiveViewFlags.VIEWPORT)
        self.assertEqual(
            set(('lcd_aspect_ratio', 'version_major', 'version_minor',
                 'viewport')),
            set(result.keys()))
        viewport = result['viewport']
        self.assertEqual(
            set(('width', 'height', 'data')), set(viewport.keys()))
        # The viewport data is a string with RGBA data, i.e., four bytes
        # per pixel.
        self.assertEqual(
            viewport['width'] * viewport['height'] * 3, len(viewport['data']))

        # Overlay bitmap and viewport can be retrieved in one call.
        result = camera.chdkGetLiveData(
            ptp.LiveViewFlags.VIEWPORT | ptp.LiveViewFlags.BITMAP)
        self.assertEqual(
            set(('lcd_aspect_ratio', 'version_major', 'version_minor',
                 'bitmap', 'viewport')),
            set(result.keys()))

        # Images can scaled to half width or double height.
        result_2 = camera.chdkGetLiveData(
            ptp.LiveViewFlags.VIEWPORT | ptp.LiveViewFlags.BITMAP |
            ptp.LiveViewFlags.DOUBLE_BITMAP_LINES |
            ptp.LiveViewFlags.DOUBLE_VIEWPORT_LINES)
        self.assertEqual(
            result['bitmap']['width'], result_2['bitmap']['width'])
        self.assertEqual(
            result['bitmap']['height'] * 2, result_2['bitmap']['height'])
        self.assertEqual(
            result['viewport']['width'], result_2['viewport']['width'])
        self.assertEqual(
            result['viewport']['height'] * 2, result_2['viewport']['height'])

        result_2 = camera.chdkGetLiveData(
            ptp.LiveViewFlags.VIEWPORT | ptp.LiveViewFlags.BITMAP |
            ptp.LiveViewFlags.SHRINK_BITMAP_LINES |
            ptp.LiveViewFlags.SHRINK_VIEWPORT_LINES)
        self.assertEqual(
            result['bitmap']['width'], result_2['bitmap']['width'] * 2)
        self.assertEqual(
            result['bitmap']['height'], result_2['bitmap']['height'])
        self.assertEqual(
            result['viewport']['width'], result_2['viewport']['width'] * 2)
        self.assertEqual(
            result['viewport']['height'], result_2['viewport']['height'])

    def chdk_upload_download_test(self, camera):
        name = tempfile.mktemp()
        test_text = ''.join(
            chr(random.randrange(32, 254)) for i in range(100))
        f = open(name, 'w')
        f.write(test_text)
        f.close()
        remote_file_name = r'A/test'
        camera.chdkUpload(name, remote_file_name)
        name_2 = tempfile.mktemp()
        camera.chdkDownload(remote_file_name, name_2)
        result = open(name_2).read()
        self.assertEqual(test_text, result)

        camera.chdkUploadString(test_text, 'A/test_2')
        result = camera.chdkDownloadString('A/test_2')
        self.assertEqual(test_text, result)

    def get_thumbnail_test(self, camera, expected):
        for h in camera.getObjectHandles(-1):
            info = camera.getObjectInfo(h)
            if info['object_format'] in (
                ptp.ObjectFormat.EXIF_JPEG,
                ptp.ObjectFormat.TIFF_EP,
                ptp.ObjectFormat.FlashPix,
                ptp.ObjectFormat.BMP,
                ptp.ObjectFormat.CIFF,
                ptp.ObjectFormat.Undefined_0x3806,
                ptp.ObjectFormat.GIF,
                ptp.ObjectFormat.JFIF,
                ptp.ObjectFormat.PCD,
                ptp.ObjectFormat.PICT,
                ptp.ObjectFormat.PNG,
                ptp.ObjectFormat.Undefined_0x380C,
                ptp.ObjectFormat.TIFF,
                ptp.ObjectFormat.TIFF_IT,
                ptp.ObjectFormat.JP2,
                ptp.ObjectFormat.JPX,
                ptp.ObjectFormat.EK_M3U):
                camera.getThumbnail(h)
            else:
                if not getattr(
                    expected, 'SKIP_THUMBNAIL_TEST_FOR_NON_IMAGE_OBJECT',
                    False):
                    self.assertRaises(ptp.PTPError, camera.getThumbnail, h)

    optests = {
        # Seems to be OK for test_devicecontroller
        ptp.OperationCode.GetStorageIDs: storage_ids_test,
        ptp.OperationCode.GetStorageInfo: storage_info_test,
        # XXX The tests below confuses the camera in test_devicecontroller.py.
        # Exact reason unknown...
        #ptp.OperationCode.GetObjectHandles: object_handles_test,
        #ptp.OperationCode.GetObjectInfo: object_info_test,
        #ptp.OperationCode.GetObject: get_object_test,
        #ptp.OperationCode.GetThumb: get_thumbnail_test,
        ptp.OperationCode.CHDK: chdk_test,
        }
