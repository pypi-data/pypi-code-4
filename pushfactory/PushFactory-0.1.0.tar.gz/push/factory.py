from push.apple import APN
from push.google import C2DM, GCM

class PushFactory(object):

	@staticmethod
	def create(**data):
		type = data['type'].lower()
		if type == 'apn':
			return APN(**data)
		elif type == 'c2dm':
			return C2DM(**data)
		elif type == 'gcm':
			return GCM(**data)
		else:
			return None
