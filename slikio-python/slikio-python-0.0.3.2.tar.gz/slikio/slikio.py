import requests
import json

class SlikIO:
	"""Initializes a SlikIO object, takes a private api key"""
	def __init__(self, private_key):
		self.private_key = private_key
		self.base_url = "https://{0}:@app.slik.io/api/v1/".format(private_key)

	"""Pushes given data to a collection"""
	def sendData(self, collection_id, data):
		url = "collections/{0}/data".format(collection_id)
		return self.__makePOSTRequest(url, data)

	"""Makes a POST response to a specified API endpoint with specified data
	Returns the response object"""
	def __makePOSTRequest(self, url, data):
		data = json.dumps({"data": data})
		headers = {'Content-Type': 'application/json'}
		response = requests.post(self.base_url+url, data=data,headers=headers)
		return response
