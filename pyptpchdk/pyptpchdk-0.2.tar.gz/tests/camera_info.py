# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

# Information about specific cameras

__metaclass__ = type

import ptp
import re
import subprocess
import sys
from testtools.matchers import Mismatch
from testtools.testcase import TestSkipped
from unittest import skipIf, skipUnless


def check_set_integer_property(camera, property, min_value, max_value):
    current_value = property.value
    if property.constraint is None:
        property.value = min_value
        property.value = max_value
        try:
            value = min_value - 1
            return Mismatch(
                "Checking access to property %i of %s: "
                "Can set value below the supposed minimum value (%i)."
                % (property.id, camera.model, min_value))
        except PTPError:
            pass
        try:
            value = max_value + 1
            return Mismatch(
                "Checking access to property %i of %s: "
                "Can set value above the supposed minimum value (%i)."
                % (property.id, camera.model, max_value))
        except PTPError:
            pass
        property.value = current_value
        return
    constraint = property.constraint
    if isinstance(constraint, tuple):
        for value in constraint:
            property.value = value
    else:
        min_val, max_val, step = constraint
        if (min_val > max_val):
            return Mismatch(
                "Checking access to property %i of %s: "
                "Range constraint minimum (%s) is larger than maximum (%s)."
                % (property.id, camera.model, min_val, max_val))
        value = min_val
        while value <= max_val:
            property.value = value
            value += step
    property.value = current_value
    return None

def check_set_string_property(camera, property):
    value = property.value
    property.value = ''
    new_value = property.value
    if new_value != '':
        return Mismatch(
            "Could not change property %i.\n"
            "Expected '' but got %r" % (property.id, new_value))
    property.value = value

set_value_checkers = {
    # PTP_DTC_INT8
    1: (lambda camera, property:
            check_set_integer_property(camera, property, -128, 127)),
    # PTP_DTC_UINT8
    2: (lambda camera, property:
            check_set_integer_property(camera, property, 0, 255)),
    # PTP_DTC_INT16
    3: (lambda camera, property:
            check_set_integer_property(camera, property, -2**15, 2**15-1)),
    # PTP_DTC_UINT16
    4: (lambda camera, property:
            check_set_integer_property(camera, property, 0, 2**16-1)),
    # PTP_DTC_INT32
    5: (lambda camera, property:
            check_set_integer_property(camera, property, -2**31, 2**31-1)),
    # PTP_DTC_UINT32
    6: (lambda camera, property:
            check_set_integer_property(camera, property, 0, 2**32-1)),
    # PTP_DTC_STR
    0xffff: check_set_string_property,
    }

def set_uint8_property(camera, property):
    """Try to set a UINT8 property."""

# if set, the related check is skipped.
NO_VALUE_ACCESS_CHECK = 1
NO_VALUE_CHANGE_CHECK = 2
NO_DEFAULT_VALUE_COMPARISON = 4

class BaseDevicePropertyMatcher:
    def __init__(self, camera_info, prop_id, readonly, default, constraint,
                 datatype, flags=0):
        self.camera_info = camera_info
        self.prop_id = prop_id
        self.readonly = readonly
        self.default = default
        self.constraint = constraint
        self.datatype = datatype
        self.flags = flags

    def checkReadOnly(self, camera, property):
        if property.readonly != self.readonly:
            return Mismatch(
                "Checking access to property %i of %s: "
                "readonly mismatch. Expected %r, got %r"
                % (self.prop_id, camera.model, self.readonly,
                   property.readonly))
        return None

    def checkDefault(self, camera, property):
        if self.flags & NO_DEFAULT_VALUE_COMPARISON:
            # just check access
            property.default
            return
        if property.default != self.default:
            return Mismatch(
                "Checking access to property %i of %s: "
                "default value mismatch. Expected %r, got %r"
                % (self.prop_id, camera.model, self.default,
                   property.default))
        return None

    def checkConstraint(self, camera, property):
        if property.constraint != self.constraint:
            return Mismatch(
                "Checking access to property %i of %s: "
                "constraint mismatch. Expected %r, got %r"
                % (self.prop_id, camera.model, self.constraint,
                   property.constraint))
        return None

    def checkDatatype(self, camera, property):
        if property.type != self.datatype:
            return Mismatch(
                "Checking access to property %i of %s: "
                "datatype mismatch. Expected %r, got %r"
                % (self.prop_id, camera.model, self.datatype,
                   property.type))
        return None

    def checkValueAccess(self, camera, property):
        if self.flags & NO_VALUE_ACCESS_CHECK:
            return
        property.value

    def checkSetValue(self, camera, property):
        if self.flags & NO_VALUE_CHANGE_CHECK or property.readonly:
            return
        return set_value_checkers[property.type](camera, property)

    def match(self, camera):
        # Each property should provide an ID, a readonly flag,
        # a default value, a current value and a constraint.
        try:
            property = camera.getDeviceProperty(self.prop_id)
            if property.id != self.prop_id:
                return Mismatch(
                    "Checking access to property %i of %s: "
                    "returned property has ID %i"
                    % (self.prop_id, camera.model, property.id))
            mismatch = self.checkDatatype(camera, property)
            if mismatch:
                return mismatch
            # checking more details only makes sesne for properties we can
            # handle.
            if property.type in set_value_checkers:
                for check in (self.checkReadOnly, self.checkDefault,
                              self.checkConstraint, self.checkValueAccess,
                              self.checkSetValue):
                    mismatch = check(camera, property)
                    if mismatch:
                        return mismatch
            return None
        except Exception, err:
            # we need a bit more information about this exception:
            print >>sys.stderr, (
                "Error checking property %i of camera %s:"
                % (self.prop_id, camera.model))
            raise

    def __str__(self):
        return "%s for property %s of %s" % (
            self.__class__.__name__, self.prop_id, self.camera_info.model)


class VaryingDefaultPropertyMatcher(BaseDevicePropertyMatcher):
    """May sound odd, but the default value _can_ change..."""
    def checkDefault(self, camera, property):
        if self.flags & NO_DEFAULT_VALUE_COMPARISON:
            # just check access
            property.default
            return
        if property.default not in self.default:
            return Mismatch(
                "Checking access to property %i of %s: "
                "default value mismatch. Expected one of %r, got %r"
                % (self.prop_id, camera.model, self.default,
                   property.default))
        return None


class PropertyMatcherNotImplementedProperty(object):
    """More a documentation that things are not complete:

    Assert that attempts to access the given property raises
    an exception.
    """
    def __init__(self, camera_info, prop_id):
        self.camera_info = camera_info
        self.prop_id = prop_id

    def match(self, camera):
        try:
            camera.getDeviceProperty(self.prop_id)
        except ptp.PTPError, exc:
            if str(exc).startswith("Can't (yet) access properties of type "):
                return None
            return Mismatch(
                "Checking access to property %i of %s: "
                "Expected PTPError for not implemented property "
                "but got PTPError %s"
                % (self.prop_id, camera_info.model, exc))
        return Mismatch(
            "Expected an exception accessing property %i of %s "
            "but access to this property was successful. Update the tests."
            % (self.prop_id, camera_info.model))

    def __str__(self):
        return "BaseDevicePropertyMatcher for property %s of %s" % (
            self.prop_id, self.camera_info.model)


class FakeMatcher:
    """CameraInfo.matchProperty() must return some kind of matcher.

    If no specific CameraInfo class is available, there is no way
    to figure out what to match against.
    """
    def __init__(self, camera_info, prop_id):
        self.camera_info = camera_info
        self.prop_id = prop_id

    def match(self, camera):
        raise TestSkipped(
            '%s does not test anything: Define a CameraInfo class and '
            'property matchers for this device.' % self)

    def __str__(self):
        return "FakeMatcher for property %s" % self.prop_id


class CameraInfo:
    """Just a marker."""
    # Override for dynamically generated classes.
    known_camera = True

    # default for unknown cameras.
    prop_matcher = {}

    @classmethod
    def matchProperty(cls, prop_id):
        """Return a matcher for the given property."""
        matcher, params = cls.prop_matcher.get(prop_id, (None, None))
        if matcher is not None:
            return matcher(cls, prop_id, *params)
        return FakeMatcher(cls, prop_id)


# define a class for a camera about which we have no real information.
def makeGenericCamera(vendor_id, product_id):
    cls = type(
        'Camera_%04x_%04x' % (vendor_id, product_id), (CameraInfo,),
        {'vendor_id': vendor_id,
         'product_id': product_id,
         'known_camera': False
         })
    known_cameras[(vendor_id, product_id)] = cls
    return cls


class CanonSX100IS(CameraInfo):
    vendor_id = 0x04a9
    product_id = 0x315e
    model = 'Canon PowerShot SX100 IS'
    capture_formats = [ptp.ObjectFormat.EXIF_JPEG, #14337
                       ]
    functional_mode = 0
    image_formats = [
        ptp.ObjectFormat.Association, #12289
        ptp.ObjectFormat.Script, #12290
        ptp.ObjectFormat.DPOF, #12294
        # xxx WAV in a camera???
        ptp.ObjectFormat.WAV, #12296
        ptp.ObjectFormat.AVI, #12298
        14336,
        ptp.ObjectFormat.EXIF_JPEG, #14337
        45313, 45315, 48897]
    standard_version = 100
    supported_device_properties = [
        53250,
        ptp.PropertyID.CANON_ViewfinderMode, #53251
        ptp.PropertyID.CANON_SizeQualityMode, #53292
        53293, 53294, 53295, 53296,
        ptp.PropertyID.CANON_FlashMemory, #53297
        ptp.PropertyID.CANON_CameraModel, #53298
        ptp.PropertyID.CANON_CameraOwner, #53299
        ptp.PropertyID.CANON_UnixTime, #53300
        53317, 53318, 53319, 53320, 53321, 53322, 53328, 54274, 54278,
        54279]
    supported_operations = [
        ptp.OperationCode.GetDeviceInfo, #4097
        ptp.OperationCode.OpenSession, #4098
        ptp.OperationCode.CloseSession, #4099
        ptp.OperationCode.GetStorageIDs, #4100
        ptp.OperationCode.GetStorageInfo, #4101
        ptp.OperationCode.GetNumObjects, #4102
        ptp.OperationCode.GetObjectHandles, #4103
        ptp.OperationCode.GetObjectInfo, #4104
        ptp.OperationCode.GetObject, #4105
        ptp.OperationCode.GetThumb, #4106
        ptp.OperationCode.DeleteObject, #4107
        ptp.OperationCode.SendObjectInfo, #4108
        ptp.OperationCode.SendObject, #4109
        ptp.OperationCode.InitiateCapture, #4110
        ptp.OperationCode.FormatStore, #4111
        ptp.OperationCode.SetObjectProtection, #4114
        ptp.OperationCode.GetDevicePropDesc, #4116
        ptp.OperationCode.GetDevicePropValue, #4117
        ptp.OperationCode.SetDevicePropValue, #4118
        ptp.OperationCode.ResetDevicePropValue, #4119
        ptp.OperationCode.GetPartialObject, #4123
        ptp.OperationCode.CANON_GetObjectSize, #36865
        36866, 36870,
        ptp.OperationCode.CANON_StartShootingMode, #36872
        ptp.OperationCode.CANON_EndShootingMode, #36873
        ptp.OperationCode.CANON_ViewfinderOn, #36875
        ptp.OperationCode.CANON_ViewfinderOff, #36876
        ptp.OperationCode.CANON_ReflectChanges, #36877
        36882,
        ptp.OperationCode.CANON_CheckEvent, #36883
        ptp.OperationCode.CANON_FocusLock, #36884
        ptp.OperationCode.CANON_FocusUnlock, #36885
        36888, 36889,
        ptp.OperationCode.CANON_InitiateCaptureInMemory, #36890
        ptp.OperationCode.CANON_GetPartialObject, #36891
        36892,
        ptp.OperationCode.CANON_GetViewfinderImage, #36893
        36894, 36895,
        ptp.OperationCode.CANON_GetFolderEntries, #36897
        36899, 36900, 36901, 36904, 36905, 36906, 36907, 36908, 36909, 36910,
        36916, 36920, 36921, 36922, 36923, 36927, 36928, 36929, 36932, 36933,
        36939, 36940, 36941, 36942, 36943, 36948, 36949, 36950, 38913, 38914,
        38915, 38916, 38917,
        ptp.OperationCode.CHDK, #39321
        ]
    vendor = 'Canon Inc.'

    # reference values for type 16386, 16390 are most likely wrong: it is
    # and array, and that's not yet supported.
    prop_matcher = {
        # params: readonly, default, datatype, flags
        # xxxxxx odd: We can't yet change _any_ property. This indicates
        # either a bug, or we must change the camera mode?
        53250: (BaseDevicePropertyMatcher, (True, 0, (0, 1, 2, 3, 4, 5), 4)),
        ptp.PropertyID.CANON_ViewfinderMode:
            (BaseDevicePropertyMatcher, (True, 1, (0, 1, 2, 3), 6)),
        ptp.PropertyID.CANON_SizeQualityMode:
            (BaseDevicePropertyMatcher, (True, None, None, 16390)),
        53293: (BaseDevicePropertyMatcher, (True, None, None, 16390)),
        53294: (BaseDevicePropertyMatcher, (True, 524288, None, 6)),
        53295: (BaseDevicePropertyMatcher, (True, 262144, None, 6)),
        53296: (BaseDevicePropertyMatcher, (True, 256, None, 6)),
        ptp.PropertyID.CANON_FlashMemory:
            (BaseDevicePropertyMatcher, (True, 16777216, None, 6)),
        ptp.PropertyID.CANON_CameraModel:
            (BaseDevicePropertyMatcher, (True, model, None, 65535)),
        ptp.PropertyID.CANON_CameraOwner:
            (BaseDevicePropertyMatcher, (True, None, None, 16386)),
        ptp.PropertyID.CANON_UnixTime:
            (BaseDevicePropertyMatcher, (False, 1314056841, None,
                                            6, NO_DEFAULT_VALUE_COMPARISON |
                                               NO_VALUE_CHANGE_CHECK)),
        53317: (BaseDevicePropertyMatcher, (False, 2, (1, 2, 3, 4, 5, 6, 7),
                                            4)),
        53318: (BaseDevicePropertyMatcher, (True, 257, None, 4)),
        53319: (BaseDevicePropertyMatcher, (True, 0, None, 4)),
        53320: (BaseDevicePropertyMatcher, (True, None, None, 16390)),
        53321: (BaseDevicePropertyMatcher, (True, 36241408, None, 6)),
        53322: (BaseDevicePropertyMatcher, (False, 0, (0, 1, 2, 3), 2)),
        53328: (BaseDevicePropertyMatcher, (True, 0, None, 2)),
        54274: (BaseDevicePropertyMatcher, (True, model, None, 65535)),
        # Changing this property does indeed not work for the SX100.
        54278: (BaseDevicePropertyMatcher, (False, 'Windows', None, 65535,
                                            NO_VALUE_CHANGE_CHECK)),
        54279: (BaseDevicePropertyMatcher, (True, 1, None, 6)),
        }


class CanonSX30IS(CameraInfo):
    vendor_id = 0x04a9
    product_id = 0x3210
    model = 'Canon PowerShot SX30 IS'
    capture_formats = [ptp.ObjectFormat.EXIF_JPEG, #14337
                       ]
    functional_mode = 0
    image_formats = [
        ptp.ObjectFormat.Association, #12289
        ptp.ObjectFormat.Script, #12290
        ptp.ObjectFormat.DPOF, #12294
        # xxx WAV in a camera???
        ptp.ObjectFormat.WAV, #12296
        ptp.ObjectFormat.AVI, #12298
        14336,
        ptp.ObjectFormat.EXIF_JPEG, #14337
        45313, 45315, 45316, 45317, 48897]
    standard_version = 100
    supported_device_properties = [
        ptp.PropertyID.BatteryLevel,
        53250,
        ptp.PropertyID.CANON_ViewfinderMode, #53251
        53294, 53295, 53296, 53297, 53298, 53299, 53300,
        ptp.PropertyID.CANON_D045, #53317,
        53318, 53319, 53321, 53322, 53328, 53329, 54019, 54274, 54278,
        54279]
    supported_operations = [
        ptp.OperationCode.GetDeviceInfo, #4097
        ptp.OperationCode.OpenSession, #4098
        ptp.OperationCode.CloseSession, #4099
        ptp.OperationCode.GetStorageIDs, #4100
        ptp.OperationCode.GetStorageInfo, #4101
        ptp.OperationCode.GetNumObjects, #4102
        ptp.OperationCode.GetObjectHandles, #4103
        ptp.OperationCode.GetObjectInfo, #4104
        ptp.OperationCode.GetObject, #4105
        ptp.OperationCode.GetThumb, #4106
        ptp.OperationCode.DeleteObject, #4107
        ptp.OperationCode.SendObjectInfo, #4108
        ptp.OperationCode.SendObject, #4109
        ptp.OperationCode.FormatStore, #4111
        ptp.OperationCode.SetObjectProtection, #4114
        ptp.OperationCode.GetDevicePropDesc, #4116
        ptp.OperationCode.GetDevicePropValue, #4117
        ptp.OperationCode.SetDevicePropValue, #4118
        ptp.OperationCode.ResetDevicePropValue, #4119
        ptp.OperationCode.GetPartialObject, #4123
        ptp.OperationCode.CANON_GetObjectSize, #36865
        36866, 36870, 36878, 36879, 36880, 36881,
        ptp.OperationCode.CANON_CheckEvent, #36883
        36889,
        ptp.OperationCode.CANON_GetPartialObject, #36891
        36892, 36894, 36895,
        ptp.OperationCode.CANON_GetFolderEntries, #36897
        36900, 36901,
        36920, 36921, 36922, 36923, 36939, 36940, 36944, 36945, 36956,
        36957, 36960, 36962, 38913, 38914, 38915, 38916, 38917,
        ptp.OperationCode.CHDK, #39321
        ]
    vendor = 'Canon Inc.'

    # reference values for type 16386, 16390 are most likely wrong: it is
    # and array, and that's not yet supported.
    prop_matcher = {
        # params: readonly, default, constraint, datatype, flags
        ptp.PropertyID.BatteryLevel:
            (BaseDevicePropertyMatcher, (True, 3, (0, 1, 2, 3), 2)),
        # XXX default value is 0 only when an external power supply is
        # used instead of a battrey. WIth a battery, the default value is
        # 1.
        53250: (BaseDevicePropertyMatcher, (True, 1, (0, 1, 2, 3, 4, 5), 4)),
        ptp.PropertyID.CANON_ViewfinderMode:
            (BaseDevicePropertyMatcher, (True, 1, (0, 1, 2, 3), 6)),
        53294: (BaseDevicePropertyMatcher, (True, 524288, None, 6)),
        53295: (BaseDevicePropertyMatcher, (True, 524288, None, 6)),
        53296: (BaseDevicePropertyMatcher, (True, 256, None, 6)),
        ptp.PropertyID.CANON_FlashMemory: # 53297
            (BaseDevicePropertyMatcher, (True, 16777216, None, 6)),
        ptp.PropertyID.CANON_CameraModel: # 53298
            (BaseDevicePropertyMatcher, (True, model, None, 65535)),
        ptp.PropertyID.CANON_CameraOwner: # 53299
            (BaseDevicePropertyMatcher, (True, None, None, 16386)),
        ptp.PropertyID.CANON_UnixTime: #53300
            (BaseDevicePropertyMatcher, (False, 1314056841, None,
                                         6, NO_DEFAULT_VALUE_COMPARISON |
                                            NO_VALUE_CHANGE_CHECK)),
        53317: (BaseDevicePropertyMatcher, (False, 2, (1, 2, 3, 4, 5, 6, 7),
                                            4)),
        53318: (BaseDevicePropertyMatcher, (True, 257, None, 4)),
        53319: (BaseDevicePropertyMatcher, (True, 2, None, 4)),
        53321: (BaseDevicePropertyMatcher, (True, 43188224, None, 6)),
        53322: (BaseDevicePropertyMatcher, (False, 0, (0, 1, 2, 3), 2)),
        # The value of this property seems to change from 0 to 1
        # whenever another property is changed.
        53328: (VaryingDefaultPropertyMatcher, (True, (0, 1), None, 2)),
        53329: (BaseDevicePropertyMatcher, (True, 0, None, 16388)),
        54019: (BaseDevicePropertyMatcher, (True, 1, None, 2)),
        54274: (BaseDevicePropertyMatcher, (True, model, None, 65535)),
        54278: (BaseDevicePropertyMatcher, (False, 'Windows', None, 65535)),
        54279: (BaseDevicePropertyMatcher, (True, 1, None, 6)),
        }

    # special flags
    # A later call to PTPDevice.chdkScriptSupport() fails for the SX30.
    SKIP_THUMBNAIL_TEST_FOR_NON_IMAGE_OBJECT = True


class CanonEOS400D(CameraInfo):
    vendor_id = 0x04a9
    product_id = 0x3110
    model = 'Canon EOS 400D DIGITAL'
    capture_formats = [14337, ]
    functional_mode = 0
    image_formats = [
        12289, 12290, 12296, 12298, 14336, 14337, 45313, 45315, 48898]
    standard_version = 100
    supported_device_properties = [53317, 53321, 53322, 54274, 54278, 54279]
    supported_operations = [
        4097, 4098, 4099, 4100, 4101, 4102, 4103, 4104, 4105, 4106, 4107,
        4108, 4109, 4111, 4116, 4117, 4118, 4123, 36883, 36895, 37121, 37122,
        37123, 37124, 37125, 37126, 37127, 37128, 37129, 37130, 37131, 37132,
        37134, 37135, 37136, 37139, 37140, 37141, 37142, 37143, 37144, 37146,
        37147, 37148, 37149, 37150, 37151, 37152, 37153, 37374, 37375, 38913,
        38914, 38915, 38916, 38917]
    vendor = 'Canon Inc.'

    # reference values for type 16386, 16390 are most likely wrong: it is
    # and array, and that's not yet supported.
    prop_matcher = {
        # params: readonly, default, datatype, flags
        53317: (BaseDevicePropertyMatcher, (False, 2, (1, 2, 3, 4, 5, 6, 7),
                                            4)),
        54274: (BaseDevicePropertyMatcher, (True, model, None, 65535)),
        54278: (BaseDevicePropertyMatcher, (False, 'Unknown Initiator', None,
                                            65535)),
        54279: (BaseDevicePropertyMatcher, (True, 1, None, 6)),
        53321: (BaseDevicePropertyMatcher, (True, 2147484214, None, 6)),
        53322: (BaseDevicePropertyMatcher, (False, 0, (0, 1, 2, 3), 2)),
        }
module = sys.modules[__name__]
known_cameras = {}

for name in module.__dict__.keys():
    obj = getattr(module, name)
    try:
        is_camera_info = issubclass(obj, CameraInfo) and not obj is CameraInfo
    except TypeError:
        # issubclass() raises this error when called on objects that are
        # not classes.
        continue
    if is_camera_info:
        id = (obj.vendor_id, obj.product_id)
        if id in known_cameras:
            raise ValueError(
                "IDs (%04x, %04x) used more than once" % id)
        known_cameras[id] = obj

connected_cameras = {}
# look for a line like
#     bInterfaceClass   6

is_imaging_device = re.compile('bInterfaceClass +6')

# lsusb -v can be a bit noisy, we may get lots of "Operation not permitted"
# messages. For now, that's not very interesting.
# xxx It might make to optionally report these errors later.
process = subprocess.Popen(
    ['lsusb',  '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
all_output, errors = process.communicate()
for device_info in all_output.strip().split('\n\n'):
    id_info = device_info[:device_info.find('\n')].split(' ', 6)
    bus_no = int(id_info[1])
    # strip a trailing ':'
    device_no = int(id_info[3][:-1])
    vendor_id, product_id = [
        int(string, 16) for string in id_info[5].split(':')]
    if is_imaging_device.search(device_info):
        if (vendor_id, product_id) in known_cameras:
            connected_cameras[(bus_no, device_no)] = (
                known_cameras[(vendor_id, product_id)])
        else:
            connected_cameras[(bus_no, device_no)] = makeGenericCamera(
                vendor_id, product_id)

def skipWithoutCamera():
    return skipUnless(connected_cameras, 'Requires at least one camera.')

def skipWithCamera():
    return skipIf(
        connected_cameras, 'Disconnect all cameras to run this test.')
