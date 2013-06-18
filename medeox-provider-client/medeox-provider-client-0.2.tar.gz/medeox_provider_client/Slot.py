from utils import toDateString, toTimeString
class Slot:
	def __init__(self, datetime, duration):
		self.datetime = datetime
		self.duration = duration # 30 (minutes)

	def toSerializableObject(self):
		return {'date': toDateString(self.datetime), 'start':toTimeString(self.datetime), 'duration':self.duration}

class SlotsType:
	BUSY = 'busy'
	FREE = 'free'