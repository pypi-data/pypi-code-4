from utils import toDatetime

class Appointment:
	def __init__(self, payload):
		self.medeoxAppointmentId = payload['id']
		self.startDatetime = toDatetime(payload['startDate'])
		self.duration = payload['duration']
		self.scheduleId = payload['scheduleId']
		self.comments = payload.get('comments', None)
		self.firstVisit = payload['firstVisit']
		self.providerAppointmentId = payload.get('providerAptId', None)
		self.patient = Patient(payload['patient'])

class Patient:
	def __init__(self, payload):
		self.firstName = payload['firstName']
		self.lastName = payload['lastName']
		self.insurance = payload.get('insurance', None)
		self.phone = payload.get('phone', None)
		self.customFields = payload.get('customFields', None)