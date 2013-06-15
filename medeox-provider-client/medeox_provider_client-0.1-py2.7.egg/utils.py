from base64 import b64encode
from datetime import datetime
from exceptions import UnauthorizedException, InvalidInputException, NotFoundException, InternalServerException, ServiceUnavailableException

class Connection:
	def __init__(self, name ,apiKey, production):
		self.baseUrl = 'api.medeox.com' if production else 'staging.api.medeox.com'
		self.headers = {'Authorization': 'Basic ' + b64encode(name + ':' + apiKey)}

def toDate(dateValue):
	return datetime.strptime(dateValue, '%Y-%m-%d')
def toDatetime(datetimeValue):
	return datetime.strptime(datetimeValue, '%Y-%m-%dT%H:%M:%S.000Z')

def toDateString(datetime):
	return datetime.strftime('%Y-%m-%d')

def toTimeString(datetime):
	return datetime.strftime('%H:%M')

def toListOfDicts(list):
	return [ item.__dict__ for item in list]

def getErrorMessageFromResponse(response):
	json = None;
	try:
		json = response.json()
	except:
		return ''
	return json.get('error', '')
	
def handleResponseErrors(response):
	if response.status_code == 401 or response.status_code == 403:
		raise UnauthorizedException('Invalid credentials')
	elif response.status_code == 400 or response.status_code == 409:
		raise InvalidInputException(getErrorMessageFromResponse(response))
	elif response.status_code == 404:
		raise NotFoundException(getErrorMessageFromResponse(response))
	elif response.status_code == 500:
		raise InternalServerException(getErrorMessageFromResponse(response))
	elif response.status_code == 503:
		raise ServiceUnavailableException('Service temporary unavailable')