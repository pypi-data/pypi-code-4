from utils import toDateString, toTimeString
class Slot:
	def __init__(self, datetime, duration):
		self.date = toDateString(datetime)
		self.start = toTimeString(datetime)
		self.duration = duration # 30 (minutes)

class SlotType:
	BUSY = 'busy'
	FREE = 'free'