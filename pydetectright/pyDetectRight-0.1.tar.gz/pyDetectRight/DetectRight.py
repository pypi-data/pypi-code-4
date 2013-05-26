__author__ = 'chenxm'


from py4j.java_gateway import JavaGateway
from py4j.java_collections import SetConverter, MapConverter, ListConverter


class DetectRight(object):

	def __init__(self, dbstring):
		self.gateway = JavaGateway()
		self.entry = self.gateway.entry_point
		self.gateway.entry_point.initializeDetectRight(dbstring)


	def getAllDevices(self, ids = None):
		if ids == None:
			return self.entry.getAllDevices()
		else:
			java_list = ListConverter().convert(ids, self.gateway._gateway_client)
			return self.entry.getAllDevices(java_list)


	def getProfile(self, schema = None):
		if schema is None:
			return self.entry.getProfile()
		else:
			return self.entry.getProfile(schema)


	def getProfileFromDevice(self, entitytype, category, description):
		return self.entry.getProfileFromDevice(entitytype, category, description)


	def getProfileFromDeviceID(self, id):
		return self.entry.getProfileFromDeviceID(id)


	def getProfileFromHeaders(self, lhm):
		java_map = MapConverter().convert(lhm, self.gateway._gateway_client)
		return self.entry.getProfileFromHeaders(java_map)


	def getProfileFromPhoneID(self, id):
		return self.entry.getProfileFromPhoneID(str(id))


	def getProfileFromTAC(self, tac):
		return self.entry.getProfileFromTAC(tac)


	def getProfileFromUA(self, ua):
		return self.entry.getProfileFromUA(ua)


	def getProfileFromUAProfile(self, uap):
		return self.entry.getProfileFromUAProfile(uap)
