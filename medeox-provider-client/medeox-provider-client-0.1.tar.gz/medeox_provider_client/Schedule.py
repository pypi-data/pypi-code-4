class Schedule:
	def __init__(self, scheduleId, clientId, country, scheduleName = None, professionalIdNumber = None ):
		self.scheduleId = scheduleId
		self.clientId = clientId
		self.country = country # 'es'
		self.scheduleName = scheduleName
		self.professionalIdNumber = professionalIdNumber