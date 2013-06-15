from urllib import quote
import requests
from utils import Connection, toListOfDicts, handleResponseErrors
from json import dumps

class MedeoxRestClient:
	def __init__(self, name, apiKey, production = False):
		self._connection = Connection(name, apiKey, production)

	def _getSchedulesBaseUrl(self):
		return "https://" + self._connection.baseUrl + '/v1/provider/schedules/'
	def _getScheduleUrl(self, scheduleId, path):
		return self._getSchedulesBaseUrl()+ quote(scheduleId)+'/'+path
	def _getAppointmentsBaseUrl(self):
		return "https://" + self._connection.baseUrl + '/v1/provider/appointments/'
	def _getAppointmentUrl(self, providerAppointmentId):
		return self._getAppointmentsBaseUrl()+ quote(providerAppointmentId)

	def createSchedule(self, schedule):
		response = requests.post(self._getSchedulesBaseUrl(), data = schedule.__dict__, headers = self._connection.headers)
		#print jsonResponse
		handleResponseErrors(response)
		jsonResponse = response.json()
		return jsonResponse['activationKey']

	def activateSchedules(self, activationKey):
		response = requests.put(self._getSchedulesBaseUrl() +'active/', 
								data = {'activationKey':activationKey}, headers = self._connection.headers)
		#print response
		handleResponseErrors(response)

	def sendSlots(self, scheduleId, slotType, slots):
		payload = {'type':slotType, 'slots':toListOfDicts(slots)};
		headers = self._connection.headers
		headers['content-type'] = 'application/json'
		response = requests.post(self._getScheduleUrl(scheduleId,'slots/'), data = dumps(payload), headers = headers)
		handleResponseErrors(response)
		#print response
	
	def forceSync(self, scheduleId):
		response = requests.post(self._getScheduleUrl(scheduleId, 'sync'), headers = self._connection.headers)
		handleResponseErrors(response)
		#print response

	def cancelAppointment(self, providerAppointmentId):
		response = requests.delete(self._getAppointmentUrl(providerAppointmentId), headers = self._connection.headers)
		handleResponseErrors(response)
		#print response
		
	def rescheduleAppointment(self, providerAppointmentId, newStartDatetime, newDuration):
		response = requests.patch(self._getAppointmentUrl(providerAppointmentId), data = { 'newStart':newStartDatetime, 'newDuration': newDuration}, headers = self._connection.headers)
		handleResponseErrors(response)
		#print response
