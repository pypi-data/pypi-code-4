#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is distributed under the GNU General Public License version 3.
# See LICENSE.TXT for details.

'''
	Linux HID device API bindings
'''

import pyudev, os, fcntl, struct, collections
from decorator import decorator as _decorator

from . import usages

def _IOC(dir, type, nr, size):
	return nr%256 | (type%256)<<8 | (size%16384)<<16 | (dir%4)<<30
def _IO(type, nr):
	return _IOC(0, ord(type), nr, 0)
def _IOR(type, nr, struct):
	return _IOC(2, ord(type), nr, len(struct) if not isinstance(struct,int) else struct)
def _IOW(type, nr, struct):
	return _IOC(1, ord(type), nr, len(struct) if not isinstance(struct,int) else struct)
def _IOWR(type, nr, struct):
	return _IOC(3, ord(type), nr, len(struct) if not isinstance(struct,int) else struct)

class _StructMeta(type):
	@classmethod
	def __prepare__(metaclass, name, bases, **kwargs):
		return collections.OrderedDict()

	def __new__(cls, name, bases, classdict, **kwargs):
		memberdefs = [(k,v) for (k,v) in classdict.items() if not k.startswith('__') and isinstance(v, str)]
		members = [k for (k,v) in memberdefs]
		dct = { '__slots__': members, '_members': members }
		dct.update({k:v for (k,v) in classdict.items() if k not in members})
		result = type.__new__(cls, name, bases, dct)
		structstr = kwargs.get('mode', '@')+''.join(v for (k,v) in memberdefs)
		result.struct = struct.Struct(structstr)
		return result

	def __init__(cls, name, bases, classdict, *args, **kwargs):
		type.__init__(cls, name, bases, classdict)

	def __len__(cls):
		return cls.struct.size


class _Struct(metaclass=_StructMeta):
	def __new__(cls, *args, **kwargs):
		self = cls.unpack(bytes(len(cls)))
		for member, arg in zip(self._members, args):
			setattr(self, member, arg)
		for key, arg in kwargs.items():
			setattr(self, key, arg)
		return self

	def __repr__(self):
		return '{0}({1})'.format(type(self).__name__, ', '.join('{0}={1!r}'.format(member, getattr(self, member)) for member in self._members if member != '_'))

	@classmethod
	def unpack(cls, buffer):
		self = object.__new__(cls)
		data = cls.struct.unpack(buffer)
		for member, value in zip(cls._members, data):
			setattr(self, member, value)
		return self

	@classmethod
	def make_buffer(cls, tail=0):
		return bytearray(len(cls)+tail)

	def pack(self):
		return self.struct.pack(*(getattr(self, member) for member in self._members))


class hiddev_event(_Struct):
	hid = 'I'
	value = 'i'

class hiddev_devinfo(_Struct, mode='='):
	bustype = 'I'
	busnum = 'I'
	devnum = 'I'
	ifnum = 'I'
	vendor = 'H'
	product = 'H'
	version = 'H'
	_ = 'h'
	num_applications = 'I'

class hiddev_collection_info(_Struct, mode='='):
	index = 'I'
	type = 'I'
	usage = 'I'
	level = 'I'

class hiddev_report_info(_Struct, mode='='):
	report_type = 'I'
	report_id = 'I'
	report_num_fields = 'I'

class hiddev_field_info(_Struct, mode='='):
	report_type = 'I'
	report_id = 'I'
	field_index = 'I'
	maxusage = 'I'
	flags = 'I'
	physical = 'I'
	logical = 'I'
	application = 'I'
	logical_minimum = 'i'
	logical_maximum = 'i'
	physical_minimum = 'i'
	physical_maximum = 'i'
	unit_exponent = 'I'
	unit = 'I'

class hiddev_usage_ref(_Struct, mode='='):
	report_type = 'I'
	report_id = 'I'
	field_index = 'I'
	usage_index = 'I'
	usage_code = 'I'
	value = 'i'

class hiddev_string_descriptor(_Struct):
	index = 'i'
	value = '256s'

class _integer(_Struct):
	value = 'i'

HIDIOCGDEVINFO = _IOR('H', 0x03, hiddev_devinfo)
HIDIOCGVERSION = _IOR('H', 0x01, _integer)
HIDIOCAPPLICATION = _IO('H', 0x02)
HIDIOCGDEVINFO = _IOR('H', 0x03, hiddev_devinfo)
HIDIOCGNAME = lambda len: _IOC(2, ord('H'), 0x06, len)
HIDIOCGSTRING = _IOR('H', 0x04, hiddev_string_descriptor)
HIDIOCINITREPORT = _IO('H', 0x05)
HIDIOCGREPORT = _IOW('H', 0x07, hiddev_report_info)
HIDIOCSREPORT = _IOW('H', 0x08, hiddev_report_info)
HIDIOCGREPORTINFO = _IOWR('H', 0x09, hiddev_report_info)
HIDIOCGFIELDINFO = _IOWR('H', 0x0A, hiddev_field_info)
HIDIOCGUSAGE = _IOWR('H', 0x0B, hiddev_usage_ref)
HIDIOCSUSAGE = _IOW('H', 0x0C, hiddev_usage_ref)
HIDIOCGUCODE = _IOWR('H', 0x0D, hiddev_usage_ref)
HIDIOCGFLAG = _IOR('H', 0x0E, _integer)
HIDIOCSFLAG = _IOW('H', 0x0F, _integer)
HIDIOCGCOLLECTIONINDEX = _IOW('H', 0x10, hiddev_usage_ref)
HIDIOCGCOLLECTIONINFO = _IOWR('H', 0x11, hiddev_collection_info)

HID_REPORT_ID_UNKNOWN = 0xffffffff
HID_REPORT_ID_FIRST   = 0x00000100
HID_REPORT_ID_NEXT    = 0x00000200

HID_REPORT_TYPE_INPUT = 1
HID_REPORT_TYPE_OUTPUT = 2
HID_REPORT_TYPE_FEATURE = 3

@_decorator
def _need_opened(method, self, *args, **kwargs):
	if self._closed:
		raise ValueError('I/O operation on closed device.')
	if not self._opened:
		self.open()
	return method(self, *args, **kwargs)


class Unit:
	''' Unit and Exponent for physical HID values '''
	def __init__(self, unitval, unit_exponent):
		values = ((unitval&(0x0F<<i))>>i for i in range(0, 32, 4))
		self.value = unitval
		sys, length, mass, time, temp, current, luminance, reserved = (-8+(x&7) if x & 8 else x for x in values)

		self.english = 3 <= sys <= 4
		self.si = 1 <= sys <= 2

		# Length
		self.cm = self.rad = self.inch = self.deg = 0
		if sys == 1:
			self.cm = length
		elif sys == 2:
			self.rad = length
		elif sys == 3:
			self.inch = length
		elif sys == 4:
			self.deg = length

		# Mass
		self.gram = self.slug = 0
		if sys == 1 or sys == 2:
			self.gram = mass
		elif sys == 3 or sys == 4:
			self.slug = mass

		# Time
		self.second = time

		# Temperature
		self.kelvin = self.fahrenheit = 0
		if sys == 1 or sys == 2:
			self.kelvin = temp
		elif sys == 3 or sys == 4:
			self.fahrenheit = temp

		# Current
		self.ampere = current

		# Luminous Intensity
		self.candela = luminance

		# Exponent
		self.exponent = -8+(unit_exponent&7) if unit_exponent & 8 else unit_exponent

	def __repr__(self):
		return '<Unit [{0:08x}:{1:02x}] {2!r}>'.format(self.value, self.exponent, self.__str__())

	def __str__(self):
		unitval = self.value
		unit_exponent = self.exponent

		# Special cases
		if unitval == 0x010000e1 and unit_exponent == 2:
			return 'Cd'
		elif unitval == 0xe1f1 and unit_exponent == 5:
			return 'Pa'
		elif unitval == 0xe1f1 and unit_exponent == 1:
			return 'Pa'
		elif unitval == 0xe1f1 and unit_exponent == 5:
			return 'bar'
		elif unitval == 0xe1f1 and unit_exponent == 2:
			return 'mbar'
		elif unitval == 0xe111 and unit_exponent == 5:
			return 'N'
		elif unitval == 0x00204fe1 and unit_exponent == -7:
			return 'F'
		elif unitval == 0xd121 and unit_exponent == 5:
			return 'W'
		elif unitval == 0x00e0e121 and unit_exponent == 5:
			return 'H'
		elif unitval == 0x00e0e121 and unit_exponent == 5:
			return 'Ω'
		elif unitval == 0x00e0e121 and unit_exponent == 5:
			return 'Ω'
		elif unitval == 0x00f0d121 and unit_exponent == 5:
			return 'V'
		elif unitval == 0x01f0 and unit_exponent == 0:
			return 'Hz'
		elif unitval == 0x00f0e101 and unit_exponent == 0:
			return 'Gs'
		elif unitval == 0x00f0e101 and unit_exponent == -4:
			return 'T'

		units_a = []
		units_b = []

		# Length
		if self.cm:
			target = units_a if self.cm>=0 else units_b
			target.append({ 1:'cm', 2:'cm²', 3:'cm³', 4:'cm⁴' }[abs(self.cm)])
		if self.inch:
			target = units_a if self.inch>=0 else units_b
			target.append({ 1:'in', 2:'in²', 3:'in³', 4:'in⁴' }[abs(self.inch)])
		if self.rad:
			target = units_a if self.rad>=0 else units_b
			target.append({ 1:'rad', 2:'sr', 3:'rad³', 4:'sr²' }[abs(self.rad)])
		if self.deg:
			target = units_a if self.deg>=0 else units_b
			target.append({ 1:'°', 2:'(°)²', 3:'(°)³', 4:'(°)⁴' }[abs(self.deg)])

		# Mass
		if self.gram:
			target = units_a if self.gram>=0 else units_b
			target.append({ 1:'g', 2:'g²', 3:'g³', 4:'g⁴' }[abs(self.gram)])
		if self.slug:
			target = units_a if self.slug>=0 else units_b
			target.append({ 1:'slug', 2:'slug²', 3:'slug³', 4:'slug⁴' }[abs(self.slug)])

		# Time
		if self.second:
			target = units_a if self.second>=0 else units_b
			target.append({ 1:'s', 2:'s²', 3:'s³', 4:'s⁴' }[abs(self.second)])

		# Temperature
		if self.kelvin:
			target = units_a if self.kelvin>=0 else units_b
			target.append({ 1:'K', 2:'K²', 3:'K³', 4:'K⁴' }[abs(self.kelvin)])
		if self.fahrenheit:
			target = units_a if self.fahrenheit>=0 else units_b
			target.append({ 1:'°F', 2:'(°F)²', 3:'(°F)³', 4:'(°F)⁴' }[abs(self.fahrenheit)])

		# Current
		if self.ampere:
			target = units_a if self.ampere>=0 else units_b
			target.append({ 1:'A', 2:'A²', 3:'A³', 4:'A⁴' }[abs(self.ampere)])

		# Luminous Intensity
		if self.candela:
			target = units_a if self.candela>=0 else units_b
			target.append({ 1:'Cd', 2:'Cd²', 3:'Cd³', 4:'Cd⁴' }[abs(self.candela)])

		if 'cm²' in units_a and unit_exponent >= 2:
			units_a[units_a.index('cm')] = 'm²'
			unit_exponent -= 4
		elif 'cm²' in units_b and unit_exponent <= 1:
			units_b[units_b.index('cm²')] = 'm²'
			unit_exponent += 4
		elif 'cm' in units_a and unit_exponent >= 2:
			units_a[units_a.index('cm')] = 'm'
			unit_exponent -= 2
		elif 'cm' in units_b and unit_exponent <= 1:
			units_b[units_b.index('cm')] = 'm'
			unit_exponent += 2
		if 'g' in units_a and unit_exponent >= 2:
			units_a[units_a.index('g')] = 'kg'
			unit_exponent -= 3
		elif 'g' in units_b and unit_exponent <= 1:
			units_b[units_b.index('g')] = 'kg'
			unit_exponent += 3

		if unit_exponent:
			prefix = '10^{0} '.format(unit_exponent)
		else:
			prefix = ''

		if unitval&0x0F in (0,5,6,7):
			return prefix

		if not units_a and not units_b:
			return prefix
		elif units_a and not units_b:
			return prefix +' '.join(units_a)
		elif units_b and not units_a:
			return prefix +'1 / '+' '.join(units_b)
		else:
			return prefix + ' '.join(units_a)+' / '+' '.join(units_b)


usage = collections.namedtuple('usage', ['code', 'value'])

class Field:
	'''
		Report[field_index] -> Field instance

		Represents a field in a report.

		Metadata about the field can be read via attribute access:
		 field.index: Field index
		 field.flags: Field flags (as tuple)
		 field.application_usage: application usage id
		 field.physical_usage: usage id for physical values
		 field.logical_usage: usage id for logical values
		 field.physical_range: range of values if converted to physical units (min,max)
		 field.logical_range: range of logical values (min,max)
		 field.unit: unit of the physical values
		 field.usages: list of usage ids (index in list equals usage index)

		Values can be read/written using array access:
		 value = field[0]: read value for usage index 0
		 field[1] = value: write value for usage index 1
		
		Easy access to array and buffered byte fields is possible
		using field.get_array_value(), field.set_array_value(),
		field.read_bytes() and field.write_bytes().

		Remember that you need to call report.commit() for changed values
		to take effect and that you may need to call report.refresh() to
		read up-to-date values.
	'''
	FLAGS = {
		0x001: (None, 'constant'),
		0x002: ('array', 'variable'),
		0x004: (None, 'relative'),
		0x008: (None, 'wrap'),
		0x010: (None, 'nonlinear'),
		0x020: (None, 'no_preferred'),
		0x040: (None, 'null_state'),
		0x080: (None, 'volatile'),
		0x100: (None, 'buffered_bytes'),
	}

	def __init__(self, device, struct):
		self.device = device
		self.report_type = struct.report_type
		self.report_id = struct.report_id
		self.index=struct.field_index
		self.flags=tuple(v[1] if k & struct.flags else v[0] for (k,v) in sorted(self.FLAGS.items()) if (k & struct.flags) or v[0])
		self.physical_usage=struct.physical
		self.logical_usage=struct.logical
		self.application_usage=struct.application
		self.logical_range=(struct.logical_minimum, struct.logical_maximum)
		self.physical_range=(struct.physical_minimum, struct.physical_maximum)
		self.unit = Unit(struct.unit, struct.unit_exponent)
		self.usages = list(self._enumerate_usage_codes(device, struct.maxusage))

	def _enumerate_usage_codes(self, device, maxusage):
		for i in range(maxusage):
			struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, i)
			try:
				struct = device._ioctl_readwrite_struct(HIDIOCGUCODE, struct)[1]
				yield struct.usage_code
			except IOError:
				yield 0

	def __getitem__(self, usage_index) -> int:
		'''
			field[usage_index] -> int

			Fetch a value for an usage index
		'''
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, usage_index, self.usages[usage_index])
		return self.device._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)[1].value

	def __setitem__(self, usage_index, value):
		'''
			field[usage_index] = value

			Set the value for an usage index
		'''
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, usage_index, self.usages[usage_index], value=int(value))
		self.device._ioctl_write_struct(HIDIOCSUSAGE, struct)
	
	def read_bytes(self):
		length = len(self.usages)
		if self.logical_range[0] < 0 or self.logical_range[1] > 255:
			raise TypeError('{0!r} cannot be read as byte stream'.format(self))
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, 0, self.usages[0])
		result = bytearray(length)
		for i in range(length):
			struct.usage_index = i
			result[i] = self.device._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)[1].value
		return bytes(result)
	
	def write_bytes(self, data):
		if self.logical_range[0] < 0 or self.logical_range[1] > 255:
			raise TypeError('{0!r} cannot be written as byte stream'.format(self))
		if len(data) > len(self.usages):
			raise ValueError('bytestring too long')
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, 0, self.usages[0])
		for i, byte in enumerate(data):
			struct.usage_index = i
			struct.value = int(byte)
			self.device._ioctl_write_struct(HIDIOCGUSAGE, struct)
	
	def get_array_value(self):
		if 'array' not in self.flags:
			raise TypeError('{0!r} is not an array field'.format(self))
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, 0)
		index = self.device._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)[1].value
		return self.usages[index-self.logical_range[0]]
	
	def set_array_value(self, value):
		if 'array' not in self.flags:
			raise TypeError('{0!r} is not an array field'.format(self))
		struct = hiddev_usage_ref(self.report_type, self.report_id, self.index, 0, self.usages[0], self.usages.index(value)+self.logical_range[0])
		self.device._ioctl_write_struct(HIDIOCSUSAGE, struct)
	
	def __repr__(self):
		result = '<Field {0.index} ({1})'.format(self, ','.join(self.flags))
		if self.application_usage:
			result += ' application: {0},'.format(usages.getUsageName(self.application_usage, True))
		if self.physical_usage or self.physical_range[0] !=  self.physical_range[1]:
			result += ' physical: {0} ({2}-{3} {1}),'.format((usages.getUsageName(self.physical_usage)), self.unit, *self.physical_range)
		if self.logical_usage or  self.logical_range[0] !=  self.logical_range[1]:
			result += ' logical: {0} ({1}-{2}),'.format((usages.getUsageName(self.logical_usage, True)), *self.logical_range)
		if 'buffered_bytes' not in self.flags:
			return result+' usages [{0}]>'.format(', '.join(('{0}'.format(usages.getUsageName(x, True)) if x else '0' for x in self.usages )))
		else:
			return result+' usages [{0} x {1}]>'.format(len(self.usages), usages.getUsageName(self.usages[0], True))


class Report:
	'''
		hiddevice.get_{input|output|feature}(id) -> Report instance
		...

		Represents a HID device report.

		Fields can be accessed via array access or iteration.
	'''

	TYPES = {
		HID_REPORT_TYPE_INPUT: 'input',
		HID_REPORT_TYPE_OUTPUT: 'output',
		HID_REPORT_TYPE_FEATURE: 'feature',
	}

	def __init__(self, device, struct):
		self.type=struct.report_type
		self.id=struct.report_id
		self.fields = [Field(device, f) for f in device._enumerate_fields(struct)]
		self.device = device

	def __bool__(self):
		return True

	def __len__(self):
		return len(self.fields)

	def __iter__(self):
		'''
			iter(report) -> iterator(Field)

			Iterate over all fields in this report.
		'''
		return iter(self.fields)

	def __getitem__(self, index) -> Field:
		'''
			report[index] -> Field

			Get a field by field index.
		'''
		return self.fields[index]

	def commit(self):
		'''Commit all changes to field values to the device.'''
		rstruct = hiddev_report_info(self.type, self.id)
		r, rstruct = self.device._ioctl_readwrite_struct(HIDIOCSREPORT, rstruct)

	def refresh(self):
		'''Reload all field values from the device.'''
		arg = hiddev_report_info(self.type, self.id, 0)
		self.device._ioctl_write_struct(HIDIOCGREPORT, arg)

	def __repr__(self):
		return '<Report {1} {0:03} {2}>'.format(self.id, self.TYPES.get(self.type,self.type), self.fields)

class HIDDevice:

	'''
		HID Device Class
	'''

	def __init__(self, device):
		'''
			HIDDevice(device) -> new HIDDevice instance

			`device' can be a path to a device node or an udev.Device instance.
		'''
		self._opened = False
		self._closed = False
		self._file = None
		self._devinfo = None
		self._vendor_id = None
		self._model_id = None
		self._revision = None
		self._interface = None
		self._busnum = None
		self._devnum = None

		if isinstance(device, str):
			devicestr = device
			if device.startswith('/'):
				self._device_node = os.path.realpath(devicestr)
			else:
				raise ValueError('Invalid argument for HIDDevDevice(): {!r}'.format(device))
		elif hasattr(device, 'sys_path'):
			self._device_node = device.device_node
			usbdev = device.find_parent('usb', 'usb_device')
			usbif = device.find_parent('usb', 'usb_interface')
			if usbdev:
				self._vendor_id = int(usbdev['ID_VENDOR_ID'], 16)
				self._model_id = int(usbdev['ID_MODEL_ID'], 16)
				self._revision = int(usbdev['ID_REVISION'], 16)
				self._busnum = usbdev.asint('BUSNUM')
				self._devnum = usbdev.asint('DEVNUM')
			if usbif:
				self._interface = int(usbif.sys_name.rsplit('.',1)[-1])
		else:
			raise TypeError('Invalid argument for HIDDevDevice(): {!r}'.format(device))

	
	def open(self):
		'''Open the device. This happens implicity on access to most properties and methods.'''
		if self._closed:
			raise ValueError('I/O operation on closed device.')
		if self._file is None:
			self._file = open(self.device_node, 'wb+', buffering=0)
			self._opened = True
			# hiddev_usage_ref on read mode
			self._ioctl_write_struct(HIDIOCSFLAG, _integer(1))

	def close(self):
		'''Close the device. This object cannot be used afterwards.'''
		self._closed = True
		if self._opened:
			self._opened = False
			self._file.close()

	def setNonBlocking(self, nonblocking=True):
		nf = fcntl.fcntl(self.fileno(),fcntl.F_GETFL)
		if nonblocking:
			nf |= os.O_NONBLOCK
		else:
			nf &= ~os.O_NONBLOCK
		fcntl.fcntl(self.fileno(),fcntl.F_SETFL , nf )
	
	def refresh(self):
		'''Let the OS reload all report data from the HID device.'''
		fcntl.ioctl(self.fileno(), HIDIOCINITREPORT)


	def __repr__(self):
		return 'HIDDevice({0.device_node!r})'.format(self)

	def __str__(self):
		return 'HIDDEV [{0.vendor_id:04x}:{0.model_id:04x}.{0.interface}] at {0.device_node}'.format(self)	

	@property
	def device_node(self):
		'''device node string'''
		return self._device_node

	@property
	def vendor_id(self):
		'''USB device vendor id'''
		if self._vendor_id is not None:
			return self._vendor_id
		elif self._devinfo:
			return self._devinfo.vendor
		else:
			return self.get_devinfo().vendor
	@property
	def model_id(self):
		'''USB device model id'''
		if self._model_id is not None:
			return self._model_id
		elif self._devinfo:
			return self._devinfo.product
		else:
			return self.get_devinfo().product
	@property
	def revision(self):
		'''USB device revision'''
		if self._revision is not None:
			return self._revision
		elif self._devinfo:
			return self._devinfo.version
		else:
			return self.get_devinfo().version

	@property
	def interface(self):
		'''USB interface'''
		if self._interface:
			return self._interface
		elif self._devinfo:
			return self._devinfo.ifnum
		else:
			return self.get_devinfo().ifnum

	@property
	def busnum(self):
		'''USB device bus number'''
		if self._busnum is not None:
			return self._busnum
		elif self._devinfo:
			return self._devinfo.busnum
		else:
			return self.get_devinfo().busnum

	@property
	def devnum(self):
		'''USB device device number'''
		if self._devnum is not None:
			return self._devnum
		elif self._devinfo:
			return self._devinfo.devnum
		else:
			return self.get_devinfo().devnum

	@property
	def applications(self):
		'''list of application usage ids'''
		if self._devinfo:
			num = self._devinfo.num_applications
		else:
			num = self.get_devinfo().num_applications

		result = []
		for index in range(num):
			try:
				result.append(fcntl.ioctl(self.fileno(), HIDIOCAPPLICATION, index))
			except IOError:
				result.append(0)

		return tuple(result)

	@_need_opened
	def fileno(self):
		return self._file.fileno()

	@_need_opened
	def read(self) -> hiddev_usage_ref:
		'''Read one device event. This function blocks until an event happens.'''
		data = self._file.read(len(hiddev_usage_ref))
		if (data == ''):
			raise RuntimeError()
		if data is None:
			return None
		return hiddev_usage_ref.unpack(data)

	@_need_opened
	def _ioctl_read_struct(self, op, structcls):
		buffer = structcls.make_buffer()
		result = fcntl.ioctl(self.fileno(), op, buffer, True)
		return result, structcls.unpack(buffer)
	@_need_opened
	def _ioctl_readwrite_struct(self, op, struct):
		buffer = bytearray(struct.pack())
		result = fcntl.ioctl(self.fileno(), op, buffer, True)
		return result, type(struct).unpack(buffer)
	@_need_opened
	def _ioctl_write_struct(self, op, struct):
		buffer = struct.pack()
		return fcntl.ioctl(self.fileno(), op, buffer)

	def get_devinfo(self) -> hiddev_devinfo:
		'''Fetch the device information structure.'''
		return self._ioctl_read_struct(HIDIOCGDEVINFO, hiddev_devinfo)[1]

	def get_name(self) -> str:
		'''Fetch the device name.'''
		buffer = bytearray(256)
		fcntl.ioctl(self.fileno(), HIDIOCGNAME(len(buffer)), buffer, True)
		return buffer.rstrip(b'\0').decode('UTF-8')

	def get_driver_version(self) -> int:
		'''Fetch the HID driver version.'''
		return self._ioctl_read_struct(HIDIOCGVERSION, _integer)[1].value

	def get_collection_info(self, application_index) -> hiddev_collection_info:
		'''Fetch the collection information for an application index.'''
		arg = hiddev_collection_info(index=int(application_index))
		return self._ioctl_readwrite_struct(HIDIOCGCOLLECTIONINFO, arg)[1]

	def get_string_descriptor(self, index) -> str:
		'''Fetch a string descriptor from the device.'''
		arg = hiddev_string_descriptor(index=int(index))
		return self._ioctl_readwrite_struct(HIDIOCGSTRING, arg)[1].value.encode('UTF-8')

	def _enumerate_reports(self, type):
		try:
			report = hiddev_report_info(report_type=int(type), report_id=HID_REPORT_ID_FIRST)
			r, report = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, report)
			yield report
		except IOError:
			return
		while r == 0:
			try:
				report.report_id |= HID_REPORT_ID_NEXT
				r, report = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, report)
				yield report
			except IOError:
				break
		return

	def _enumerate_fields(self, report):
		field = hiddev_field_info(report_type=report.report_type, report_id=report.report_id)
		for i in range(report.report_num_fields):
			field.field_index = i
			field = self._ioctl_readwrite_struct(HIDIOCGFIELDINFO, field)[1]
			field.field_index = i
			yield field

	def inputs(self) -> "iterator(Report)":
		'''Iterate over all input reports.'''
		reports = self._enumerate_reports(HID_REPORT_TYPE_INPUT)
		for report in reports:
			yield Report(self, report)

	def get_input(self, id) -> Report:
		'''Get an input report by id.'''
		report = hiddev_report_info(report_type=HID_REPORT_TYPE_INPUT, report_id=id)
		r, report = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, report)
		return Report(self, report)

	def find_input(self, usage_code) -> "(Report, int, int)":
		'''
			Find an input report by usage code.

			Returns the Report object, the field index and the usage index matching the usage code.
		'''
		struct = hiddev_usage_ref(HID_REPORT_TYPE_INPUT, 0xffffffff, 0, 0, usage_code)
		r, struct = self._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)
		rstruct = hiddev_report_info(struct.report_type, struct.report_id)
		r, rstruct = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, rstruct)
		return Report(self, rstruct), struct.field_index, struct.usage_index

	def outputs(self) -> "iterator(Report)":
		'''Iterate over all output reports.'''
		reports = self._enumerate_reports(HID_REPORT_TYPE_OUTPUT)
		for report in reports:
			yield Report(self, report)

	def get_output(self, id) -> Report:
		'''Get an output report by id.'''
		report = hiddev_report_info(report_type=HID_REPORT_TYPE_OUTPUT, report_id=id)
		r, report = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, report)
		return Report(self, report)

	def find_output(self, usage_code) ->  "(Report, int, int)":
		'''
			Find an output report by usage code.

			Returns the Report object, the field index and the usage index matching the usage code.
		'''
		struct = hiddev_usage_ref(HID_REPORT_TYPE_OUTPUT, 0xffffffff, 0, 0, usage_code)
		r, struct = self._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)
		rstruct = hiddev_report_info(struct.report_type, struct.report_id)
		r, rstruct = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, rstruct)
		return Report(self, rstruct), struct.field_index, struct.usage_index

	def features(self) -> "iterator(Report)":
		'''Iterate over all feature reports.'''
		reports = self._enumerate_reports(HID_REPORT_TYPE_FEATURE)
		for report in reports:
			yield Report(self, report)

	def get_feature(self, id) -> Report:
		'''Get a feature report by id.'''
		report = hiddev_report_info(report_type=HID_REPORT_TYPE_FEATURE, report_id=id)
		r, report = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, report)
		return Report(self, report)

	def find_feature(self, usage_code) ->  "(Report, int, int)":
		'''
			Find a feature report by usage code.

			Returns the Report object, the field index and the usage index matching the usage code.
		'''
		struct = hiddev_usage_ref(HID_REPORT_TYPE_FEATURE, 0xffffffff, 0, 0, usage_code)
		r, struct = self._ioctl_readwrite_struct(HIDIOCGUSAGE, struct)
		rstruct = hiddev_report_info(struct.report_type, struct.report_id)
		r, rstruct = self._ioctl_readwrite_struct(HIDIOCGREPORTINFO, rstruct)
		return Report(self, rstruct), struct.field_index, struct.usage_index

def enumerate_udev(context=None) -> 'iterator(HIDDevice)':
	'''
		Enumerate all HID devices via UDev
	'''
	if not context:
		context = pyudev.Context()
	devices = context.list_devices(subsystem='usb')
	for device in devices:
		if device.sys_name.startswith('hiddev'):
			yield HIDDevice(device)
