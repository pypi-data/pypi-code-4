#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is distributed under the GNU General Public License version 3.
# See LICENSE.TXT for details.

''' Generic HID explorer GUI '''

import pyudev
import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from . import enumerate_udev, usages, HIDDevice, hiddev_usage_ref

class HIDMonitor(QSocketNotifier):

	def __init__(self, device, parent):
		super().__init__(device.fileno(), QSocketNotifier.Read, parent)
		self.device = device
		self.activated.connect(self._readFromSocket)

	eventReceived = pyqtSignal(hiddev_usage_ref, name='eventReceived')

	def _readFromSocket(self):
		event = self.device.read()
		if event:
			self.eventReceived.emit(event)

class UDevHIDDevicesMonitor(QSocketNotifier):

	def __init__(self, udev_context, parent):
		self.monitor = pyudev.Monitor.from_netlink(udev_context)
		self.monitor.filter_by(subsystem='hid')
		self.monitor.enable_receiving()
		super().__init__(self.monitor.fileno(), QSocketNotifier.Read, parent)
		self.activated.connect(self._readFromSocket)

	def _readFromSocket(self):
		it = iter(self.monitor)
		next(it)

class HIDComboBox(QComboBox):
	def __init__(self, parent):
		super().__init__(parent)
		self.context = ctx = pyudev.Context()
		self.monitor = UDevHIDDevicesMonitor(ctx, self)
		self.monitor.activated.connect(self.onUdevEvent)
		self.monitor.setEnabled(1)
		self.currentIndexChanged.connect(self._onIndexChanged)

	currentDeviceChanged = pyqtSignal(str, name='currentDeviceChanged')

	def _iconForDevice(self, device):
		icons = []
		for application in device.applications:
			page = application>>16
			usage = application&0xFFFF
			icon = ''
			if page == 0x01:
				icons.append(('preferences-desktop-peripherals', 1))
				if usage == 0x02:
					icons.append(('input-mouse', 20))
				if usage == 0x07 or usage == 0x06:
					icons.append(('input-keyboard', 25))
				if usage in (0x04, 0x05, 0x08):
					icons.append(('input-gaming', 30))
				if usage == 0x80:
					icons.append(('preferences-desktop',5))
			if page == 0x0B:
				if QIcon.hasThemeIcon('internet-telephony'):
					icons.append(('internet-telephony', 30))
				else:
					icons.append(('phone', 20))
			if page == 0x0C:
				if usage == 0x04:
					icons.append(('audio-input-microphone', 27))
				if usage == 0x05:
					icons.append(('audio-headset', 30))
				if usage == 0x06:
					icons.append(('audio-input-line', 30))
				if usage == 0x160:
					icons.append(('audio-input-line', 30))
			if page == 0x0D:
				icons.append(('input-tabled',30))
			if page == 0x03:
				icons.append(('im-user',35))
			if page == 0x84 or page == 0x85:
				icons.append(('battery', 30))
			if page == 0x90:
				icons.append(('camera-photo', 30))
			if page == 0x80:
				icons.append(('video-display', 30))
		icons = [(icon,pref) for (icon,pref) in icons if QIcon.hasThemeIcon(icon)]
		if icons:
			maxpref = max(pref for (icon,pref) in icons)
			maxpref_icons = [icon for (icon,pref) in icons if pref == maxpref]
			if len(maxpref_icons) == 1:
				return QIcon.fromTheme(maxpref_icons[0])
		return QIcon.fromTheme('drive-removable-media')

	def reload(self):
		# Remember current item
		devnode = self.itemData(self.currentIndex()) if self.currentIndex() >= 0 else None

		# Update list
		self.clear()
		for device in enumerate_udev(self.context):
			icon = self._iconForDevice(device)
			self.addItem(icon, '{0} ({1})'.format(device.get_name(), device.device_node), device.device_node)

			device.close()

		# Restore if device wasn't plugged out
		index = self.findData(devnode)
		if index >= 0:
			self.setCurrentIndex(index)

	def onUdevEvent(self):
		QTimer.singleShot(5, self.reload)

	@pyqtSlot(int)
	def _onIndexChanged(self, index):
		if index == -1:
			self.currentDeviceChanged.emit('')
		else:
			self.currentDeviceChanged.emit(self.itemData(self.currentIndex()))

	def currentDevice(self):
		return self.itemData(self.currentIndex()) if self.currentIndex() >= 0 else ''

class HIDArrayWidget(QComboBox):

	def __init__(self, report, field, parent):
		super().__init__(parent)
		self.report = report
		self.field = field

		self.addItem('None', 0 if field.logical_range[0] != 0 else field.logical_range[0]-1)
		for index, usage in enumerate(field.usages):
			value = index + field.logical_range[0]
			self.addItem(usages.getUsageName(usage, vendor=report.device.vendor_id, model=report.device.model_id), value)
		self.refresh()

		if report.type == 1:
			self.currentIndexChanged.connect(self.refresh)
		else:
			self.currentIndexChanged.connect(self.setValueByIndex)


	def refresh(self):
		value = self.field[0]
		self.setCurrentIndex(self.findData(value))

	def setValueByIndex(self, index):
		data = self.itemData(index)
		if data:
			self.field[0] = data
			self.report.commit()
		self.report.refresh()
		self.refresh()

class BufferedBytesEditorDialog(QWidget):
	def __init__(self, report, field, parent):
		super().__init__(parent)
		self.setWindowFlags(Qt.Window)
		self.hide()
		self.setWindowTitle('HID Buffered Bytes: '+usages.getUsageName(field.usages[0], vendor=report.device.vendor_id, model=report.device.model_id))
		self.report = report
		self.field = field
		layout = QGridLayout(self)
		self.setLayout(layout)
		self.editor = QTextEdit(self)
		layout.addWidget(self.editor)

	def show(self):
		super().show()
		self.loadData()

	def loadData(self):
		data = self.field.read_bytes()
		text=''.join(chr(byte) if byte > 0x19 and byte != 0x5c else '\\x{0:02X}'.format(byte) for byte in data)
		self.editor.setText(text)

class HIDBufferedBytesWidget(QPushButton):

	def __init__(self, report, field, parent):
		self.report = report
		self.field = field
		super().__init__(('Show/Edit {0} bytes' if report.type != 1 else 'Show {0} bytes').format(len(field.usages)), parent)
		self.dialog = BufferedBytesEditorDialog(report, field, self)
		self.pressed.connect(self.showDialog)

	def refresh(self):
		pass

	def showDialog(self):
		self.dialog.show()

class HIDConstantWidget(QLCDNumber):

	def __init__(self, report, field, usageindex, parent):
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
		self.report = report
		self.field = field
		self.usage = usageindex
		self.disabled = False
		self.setSegmentStyle(QLCDNumber.Flat)
		self.setDigitCount(int(math.log10(self.field.logical_range[1])+1))
		self.refresh()

	def refresh(self):
		if self.disabled:
			return
		try:
			self.display(self.field[self.usage])
		except IOError:
			self.setDigitCount(4)
			self.disabled = True
			self.setHexMode()
			self.display(65535)

class HIDBooleanWidget(QCheckBox):

	def __init__(self, report, field, usageindex, parent):
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.report = report
		self.field = field
		self.usage = usageindex
		self.refresh()
		self.stateChanged.connect(self.setValue)

	def refresh(self):
		try:
			self.setChecked(self.field[self.usage])
		except IOError:
			self.setChecked(False)

	def setValue(self, value):
		self.field[self.usage] = self.field.logical_range[1] if value else self.field.logical_range[0]
		self.report.commit()
		self.report.refresh()
		self.refresh()

class HIDVariableWidget(QWidget):

	def __init__(self, report, field, usageindex, parent):
		super().__init__(parent)
		self.report = report
		self.field = field
		self.usage = usageindex
		layout = QHBoxLayout(self)
		self.setLayout(layout)
		self.label = label = QLCDNumber(self)
		self.slider = slider = QSlider(Qt.Horizontal, self)
		layout.addWidget(slider)
		label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
		slider.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		layout.addWidget(label)

		label.setSegmentStyle(QLCDNumber.Flat)
		label.setDigitCount(int(math.log10(self.field.logical_range[1])+1))
		slider.setMinimum(self.field.logical_range[0])
		slider.setMaximum(self.field.logical_range[1])
		slider.setTickPosition(QSlider.TicksBelow)
		slider.setTracking(False)
		slider.sliderMoved.connect(label.display)
		#slider.sliderReleased.connect(self.refresh)
		slider.valueChanged.connect(self.setValue)
		self.refresh()

	def refresh(self):
		try:
			v = self.field[self.usage]
			self.label.setDecMode()
			self.label.display(v)
			self.slider.setSliderPosition(v)
		except IOError:
			self.label.setHexMode()
			self.label.display(65535)

	def setValue(self, value):
		try:
			self.field[self.usage] = value
			self.report.commit()
			self.report.refresh()
		except IOError:
			pass
		self.refresh()

class ReportWidget(QWidget):

	def __init__(self, report, parent):
		self.report = report
		super().__init__(parent)
		layout = QGridLayout(self)
		layout.setColumnMinimumWidth(0, 160)
		layout.setColumnStretch(1, 2)
		self.setLayout(layout)
		self.children = children = []
		i = 0
		for field in report:
			if 'array' in field.flags:
				text = usages.getUsageName(field.logical_usage, vendor=report.device.vendor_id, model=report.device.model_id) \
						if field.logical_usage else usages.getUsageName(field.usages[0], vendor=report.device.vendor_id, model=report.device.model_id)
				label = QLabel(text, self)
				label.setToolTip(self.makeFieldTooltip(field))
				layout.addWidget(label, i, 0)
				widget = HIDArrayWidget(report, field, self)
				children.append(widget)
				layout.addWidget(widget, i, 1)
				i += 1
			elif 'buffered_bytes' in field.flags:
				text = usages.getUsageName(field.logical_usage, vendor=report.device.vendor_id, model=report.device.model_id) \
						if field.logical_usage else usages.getUsageName(field.usages[0], vendor=report.device.vendor_id, model=report.device.model_id)
				label = QLabel(text, self)
				label.setToolTip(self.makeFieldTooltip(field))
				layout.addWidget(label, i, 0)
				widget = HIDBufferedBytesWidget(report, field, self)
				children.append(widget)
				layout.addWidget(widget, i, 1)
				i += 1
			else:
				sublayout = QVBoxLayout()
				sublayout_labels = QVBoxLayout()

				text = usages.getUsageName(field.logical_usage, vendor=report.device.vendor_id, model=report.device.model_id) if field.logical_usage else None
				if text:
					label = QLabel(text, self)
					label.setToolTip(self.makeFieldTooltip(field))
					layout.addWidget(label, i, 0)
					i += 1

				for index, usage in enumerate(field.usages):
					label = QLabel(usages.getUsageName(usage, vendor=report.device.vendor_id, model=report.device.model_id), self)
					label.setToolTip(self.makeUsageTooltip(field, index, usage))
					layout.addWidget(label, i, 0)
					flags = Qt.AlignVCenter
					if 'constant' in field.flags or report.type == 1:
						widget = HIDConstantWidget(report, field, index, self)
					elif field.logical_range == (0,1):
						widget = HIDBooleanWidget(report, field, index, self)
						flags = Qt.AlignLeft|Qt.AlignVCenter
					else:
						widget = HIDVariableWidget(report, field, index, self)

					children.append(widget)
					layout.addWidget(widget, i, 1, flags)
					i += 1

	def refresh(self):
		for child in self.children:
			child.refresh()
	
	def makeFieldTooltip(self, field):
		result = 'Report {0.id} Field {1.index} ({2})'.format(self.report, field, ','.join(field.flags))
		if field.physical_usage or field.physical_range[0] !=  field.physical_range[1]:
			result += ' physical: 0x{0:08X} ({2}-{3} {1}) '.format(field.physical_usage, field.unit, *field.physical_range)
		if field.logical_usage or field.logical_range[0] != field.logical_range[1]:
			result += ' logical: 0x{0:08X} ({1}-{2}) '.format(field.logical_usage, *field.logical_range)
		return result
	
	def makeUsageTooltip(self, field, index, usage):
		return 'Report {0.id} Field {1.index} Usage {2}: 0x{3:08X}'.format(self.report, field, index, usage)

class HIDPropertiesWidget(QWidget):

	def __init__(self, device, type, parent):
		super().__init__(parent)
		self.device = device
		self.type = type

		layout = QVBoxLayout(self)
		self.setLayout(layout)
		self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

		if type == 'input':
			reports = list(device.inputs())
		elif type == 'output':
			reports = list(device.outputs())
		elif type == 'feature':
			reports = list(device.features())

		application_widgets = {}
		self.children = {}
		for report in reports:
			application = report[0].application_usage
			group = application_widgets.get(application)
			if not group:
				name = usages.getUsageName(application, vendor=report.device.vendor_id, model=report.device.model_id)
				if (application >= 0xff000000):
					name = 'Vendor Defined [{0}]'.format(name)
				group = application_widgets[application] = QGroupBox(name, self)
				layout.addWidget(group)
				group.setLayout(QVBoxLayout())
			child = ReportWidget(report, self)
			self.children[report.id] = child
			group.layout().addWidget(child)

	def refresh(self):
		for child in self.children.values():
			child.report.refresh()
			child.refresh()
	
	def refreshReport(self, id):
		child = self.children[id]
		child.report.refresh()
		child.refresh()


class HIDDeviceTabs(QTabWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.device = None
		self.last_selected = None
		self.monitor = None
		self.timer = QTimer(self)
		self.timer.timeout.connect(self._eventHandler)
		self.timer.setSingleShot(True)

	@pyqtSlot(str)
	def setDevice(self, node):
		if self.device and self.device.device_node == node:
			pass
		elif node:
			self.clear()
			self.device = HIDDevice(node)
			self.device.setNonBlocking()
			self.device.refresh()
			for type, name in [('input', 'Inputs'), ('output', 'Outputs'), ('feature', 'Features')]:
				scrollArea = QScrollArea(self)
				self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
				widget = HIDPropertiesWidget(self.device, type, scrollArea)
				scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
				scrollArea.setFrameShape(QFrame.NoFrame)
				scrollArea.setWidgetResizable(True)
				scrollArea.setWidget(widget)
				self.addTab(scrollArea, name)
				index = self.indexOf(scrollArea)
				if len(widget.children) == 0:
					self.setTabEnabled(index,False)
			self.last_selected = None
			self._setMonitor(self.device)
		else:
			self._setMonitor(None)
			self.clear()
			self.device = None
			self.last_selected = None
	
	
	def onHidEvent(self, event):
		index = self.currentIndex()
		if index+1 == event.report_type:
			report = self.device.get_input(event.report_id)
			report.refresh()
			self.currentWidget().widget().refreshReport(event.report_id)
		if index >= 0:
			if index == 1 or index == 0:
				self.timer.start(1700)
			else:
				self.timer.start(700)
	
	def _eventHandler(self):
		widget = self.currentWidget()
		if widget:
			widget.widget().refresh()
	
	def _setMonitor(self, device):
		if device is None:
			if self.monitor is not None:
				self.monitor.setEnabled(False)
				self.monitor = None
		else:
			self.monitor = HIDMonitor(device, self)
			self.monitor.eventReceived.connect(self.onHidEvent)
			self.monitor.setEnabled(True)

class HIDExplorer(QMainWindow):

	def __init__(self):
		super().__init__()
		self.setWindowTitle('HID Device Explorer')
		self.setWindowIcon(QIcon.fromTheme('preferences-desktop-peripherals'))
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

		# Main widget
		widget = self.widget = QWidget(self)
		layout = self.layout = QVBoxLayout(widget)
		widget.setLayout(layout)
		widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
		self.setCentralWidget(widget)

		# Device Select Box
		selectbox = HIDComboBox(widget)
		layout.addWidget(selectbox)

		# Device Tabs
		tabs = HIDDeviceTabs(widget)
		layout.addWidget(tabs)

		# Connect both
		selectbox.currentDeviceChanged.connect(tabs.setDevice)
		selectbox.reload()


def main(argv=[]):
	app = QApplication(argv)
	w = HIDExplorer()
	w.show()
	return app.exec_()

if (__name__ == '__main__'):
	main()