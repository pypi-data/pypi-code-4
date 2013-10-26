#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is distributed under the GNU General Public License version 3.
# See LICENSE.TXT for details.

''' API for via USB controllable monitors '''

import hiddev, time, weakref

class ranged_value(int):
	__SLOTS__ = ['min', 'max']
	def __new__(cls, value, min, max):
		self = super().__new__(cls, value)
		self.min = min
		self.max = max
		return self
	
	def __repr__(self):
		return 'monitorcontrol.ranged_value({0}, {0.min}, {0.max})'.format(self)

class input_property:

	def __init__(self, usage_code, type=ranged_value, factor=0):
		self.usage_code = usage_code
		self.type = type
		self.factor=factor

	def __get__(self, parent, owner):
		report, field_index, usage_index = parent.hiddev.find_input(self.usage_code)
		result = report[field_index][usage_index]
		if self.factor:
			result *= 10.0**self.factor
		if self.type is not ranged_value:
			return self.type(report[field_index][usage_index])
		else:
			return self.type(report[field_index][usage_index], *report[field_index].logical_range)
	
	def __set__(self, parent, value):
		raise AttributeError()

class feature_property:

	def __init__(self, usage_code, type=ranged_value):
		self.usage_code = usage_code
		self.type = type

	def __get__(self, parent, owner):
		report, field_index, usage_index = parent.hiddev.find_feature(self.usage_code)
		report.refresh()
		if self.type is not ranged_value:
			return self.type(report[field_index][usage_index])
		else:
			return self.type(report[field_index][usage_index], *report[field_index].logical_range)

	def __set__(self, parent, value):
		report, field_index, usage_index = parent.hiddev.find_feature(self.usage_code)
		report[field_index][usage_index] = int(value)
		report.commit()

class feature_enumeration_list_property:

	def __init__(self, usage_code, code_mapping):
		self.usage_code = usage_code
		self.code_mapping_name = code_mapping
		self.code_mapping = None
		self.type = type

	def get_mapping(self, parent):
		if not self.code_mapping:
			self.code_mapping = getattr(parent, self.code_mapping_name)
		return self.code_mapping

	def find_feature(self, parent):
		for feature in parent.hiddev.features():
			if feature[0].logical_usage == self.usage_code and feature[0].usages[0] & 0xFFFF0000 == 0x00810000:
				return feature
		return None

	def __get__(self, parent, owner):
		report = self.find_feature(parent)
		return tuple(self.get_mapping(parent).get(usage, '<{0:08x}>'.format(usage)) for usage in report[0].usages)
	
	def __set__(self, parent, value):
		raise AttributeError()

class enumerated_feature_property:

	def __init__(self, usage_code, code_mapping):
		self.usage_code = usage_code
		self.code_mapping_name = code_mapping
		self.code_mapping = None
		self.code_mapping_inverse = None
		self.type = type

	def get_mapping(self, parent, inverse=False):
		if not self.code_mapping:
			self.code_mapping = getattr(parent, self.code_mapping_name)
			self.code_mapping_inverse = { v:k for k,v in self.code_mapping.items() }
		return self.code_mapping if not inverse else self.code_mapping_inverse

	def find_feature(self, parent):
		for feature in parent.hiddev.features():
			if feature[0].logical_usage == self.usage_code and feature[0].usages[0] & 0xFFFF0000 == 0x00810000:
				return feature
		return None

	def __get__(self, parent, owner):
		report = self.find_feature(parent)
		report.refresh()
		usage_value = report[0].get_array_value()
		return self.get_mapping(parent).get(usage_value, '<{0:08x}>'.format(usage_value))

	def __set__(self, parent, value):
		usage_value = self.get_mapping(parent, True).get(value)
		if not usage_value:
			if isinstance(value, str) and value.startswith('<') and value.endswith('>'):
				usage_value = int(value[1:-1], 16)
			else:
				raise ValueError('Invalid value')
		report = self.find_feature(parent)
		report[0].set_array_value(usage_value)
		report.commit()
		return


class MonitorControls:
	VENDOR=0
	MODEL=0

	INPUTS = {
		0x00810001: 'VGA1',
		0x00810002: 'VGA2',
		0x00810003: 'VGA3',
		0x00810004: 'RGB1',
		0x00810005: 'RGB2',
		0x00810006: 'RGB3',
		0x00810007: 'EVC1',
		0x00810008: 'EVC2',
		0x00810009: 'EVC3',
		0x0081000A: 'MAC1',
		0x0081000B: 'MAC2',
		0x0081000C: 'MAC3',
		0x0081000D: 'COMPOSITE1',
		0x0081000E: 'COMPOSITE2',
		0x0081000F: 'COMPOSITE3',
		0x00810010: 'SVIDEO1',
		0x00810011: 'SVIDEO2',
		0x00810012: 'SVIDEO3',
		0x00810013: 'SCART1',
		0x00810014: 'SCART2',
		0x00810015: 'SCART_RGB',
		0x00810016: 'SCART_SVIDEO',
		0x00810017: 'TUNER1',
		0x00810018: 'TUNER2',
		0x00810019: 'TUNER3',
		0x0081001A: 'YUV1',
		0x0081001B: 'YUV2',
		0x0081001C: 'YUV3',
	}

	def __new__(cls, hiddev):
		if cls is MonitorControls:
			for subcls in cls.__subclasses__():
				if hiddev.vendor_id == subcls.VENDOR and hiddev.model_id == subcls.MODEL:
					return subcls(hiddev)
		return super().__new__(cls, hiddev)

	def __init__(self, hiddev):
		self.hiddev = hiddev

	def __repr__(self):
		return '{0}({1!r})'.format(type(self).__name__, self.hiddev)

	def get_name(self):
		return self.hiddev.get_name()
	
	def get_edid(self):
		report, field_index, _ = self.hiddev.find_feature(0x00800002)
		return bytes(report[field_index].read_bytes())
	
	source = enumerated_feature_property(usage_code=0x00820060, code_mapping='INPUTS')
	sources = feature_enumeration_list_property(usage_code=0x00820060, code_mapping='INPUTS')

	brightness = feature_property(usage_code=0x00820010)
	contrast = feature_property(usage_code=0x00820012)
	red_gain = feature_property(usage_code=0x00820016)
	green_gain = feature_property(usage_code=0x00820018)
	blue_gain = feature_property(usage_code=0x0082001A)

	horizontal_position = feature_property(usage_code=0x00820020)
	vertical_position = feature_property(usage_code=0x00820030)

	horizontal_frequency = input_property(usage_code=0x008200AC, type=float)
	vertical_frequency = input_property(usage_code=0x008200AE, type=float, factor=-2)


class EizoMonitorControls(MonitorControls):
	VENDOR=0x056d
	MODEL=0x0002

	INPUTS = {
		0x00810001: 'DVI',
		0x00810002: 'VGA',
		0x00810003: 'INPUT3',
	}

	KEYS = {
		1: 'UP',
		2: 'DOWN',
		4: 'LEFT',
		8: 'RIGHT',
		16: 'MENU',
		32: 'SOURCE',
		64: 'AUTO',
		128: 'POWER',
		256: 'MANUAL',
	}

	enabled = feature_property(usage_code=0xff00002f, type=bool)

	def simulate_keypress(self, key):
		if isinstance(key, str):
			for id, k in self.KEYS.items():
				if k == key:
					key = id
		if isinstance(key, str):
			raise ValueError('invalid key: {0}'.format(key))
		report, field_index, usage_index = self.hiddev.find_feature(0xff00000f)
		report[field_index][usage_index] = key
		report.commit()

	def wait_for_keypress(self):
		while True:
			event = self.hiddev.read()
			if event.usage_code == 0xff00000f and event.value & 0x0FFF != 0: #and not (0x8000 < event.value < 0x8020):
				return self.KEYS.get(event.value & 0x0FFF, event.value & 0x0FFF)

def enumerate_udev() -> 'iterator(HIDDevice)':
	'''
		Enumerate all Monitor Control HID devices via UDev
	'''
	for dev in hiddev.enumerate_udev():
		if 0x00800001 in dev.applications:
			yield dev

if __name__ == '__main__':
	for dev in enumerate_udev():
		import code
		device = MonitorControls(dev)
		banner = '\nFound "{0}".\n\nMonitorControls object is at `device\'\n'.format(device.get_name()) \
			+'Press ^D to switch to the next Monitor device or type exit() to exit.\n'
		code.interact(banner=banner,local=locals())
