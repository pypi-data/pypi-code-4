from socketIO_client import SocketIO, BaseNamespace, SocketIOUnauthorizedException
import requests
import sys
from threading import Thread, Event
from Appointment import Appointment
from utils import Connection, toDate, toListOfDicts
from time import sleep
from exceptions import UnauthorizedException

from pprint import pprint

class MedeoxSocketsClient:
	def __init__(self, adapter, name, apiKey, production = False):
		connection = Connection(name, apiKey, production)
		self.client = _MedeoxSocketsClient(connection, adapter)
		self.client.connect()
		self.client.start()

	def sendSlots(self, scheduleId, slotType, slots, callback = None):
		payload = {'id':scheduleId, 'type':slotType, 'slots':toListOfDicts(slots)};
		self.client.emit('slots', payload, callback)
	
	def forceSync(self, scheduleId, callback = None):
		self.client.emit('forceSync', {'id':scheduleId}, callback)

	def wait(self):
		try:
			while True: sleep(1)
		except KeyboardInterrupt:
			self.client.cancel()

	def __del__(self):
		self.client.cancel()

class ScheduleAdapterBase:
	def getAvailability(self, scheduleId, start, end):
		print scheduleId, start, end
	def saveAppointment(self, appointment):
		print appointment.__dict__
	def cancelAppointment(self, appointment):
		print appointment.__dict__

class _MedeoxSocketsClient(Thread):
	daemon = True
	
	def __init__(self, connection, adapter):
		super(_MedeoxSocketsClient, self).__init__()
		self._connection = connection
		self._adapter = adapter
		self._done = Event()
		self._providerNamespace = None
		self._socketIO = None
		

	def run(self):
		while not self._done.is_set():
			sleep(5)
			if self._done.is_set(): return
			if self._socketIO == None or not(self._socketIO.connected):
				print 'Retrying connection'
				sys.stdout.flush()
				self.connect()

	def connect(self):
		self._disconnect()
		try:
			self._socketIO = SocketIO(self._connection.baseUrl, 443, secure=True, headers= self._connection.headers)
			self._providerNamespace = self._socketIO.define(_ProviderNamespace, '/provider')
			self._providerNamespace.adapter = self._adapter
			print 'Connected to Medeox'
			sys.stdout.flush()
		except SocketIOUnauthorizedException, e:
			raise UnauthorizedException('Invalid credentials')
		except Exception, e:
			print 'Connection Exception:', e
			print 'Retrying in 5 seconds'
			sys.stdout.flush()
	def emit(self, messageName, payload, callback = None):
		if not(self._providerNamespace): return
		self._providerNamespace.emit(messageName, payload, callback)

	def cancel(self):
		self._disconnect()
		self._done.set()	

	def _disconnect(self):
		try:
			if self._socketIO: self._socketIO.disconnect(close=False)
		except Exception:
			pass	

class _ProviderNamespace(BaseNamespace):
	def on_availabilityRequest(self, payload):
		slots = self.adapter.getAvailability(payload['id'], toDate(payload['startDate']), toDate(payload['endDate']))
		payload['slots'] = toListOfDicts(slots)
		self.emit('availabilityResponse', payload)

	def on_appointment(self, payload):
		response = {'id': payload['id'], 'result': 'F' }
		appointment = Appointment(payload)
		ok = False
		if payload['status'] == 'N':
			#new
			result  = self.adapter.saveAppointment(appointment)
			if len(result) > 0:
				ok = result[0]
				if len(result) > 1:
					response['providerAptId'] = result[1]
		else:
			#cancelled
			ok = self.adapter.cancelAppointment(appointment)

		if ok : response['result'] = 'S'			
		self.emit('appointmentProcessed', response)