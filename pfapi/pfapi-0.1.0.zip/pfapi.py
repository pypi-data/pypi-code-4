import urllib, httplib, urlparse

_PF_API_VERSION = "1.0"
_PF_BASE_URL = "pageformant.de"
_PF_API_URL = "/api/betreiber/nvp/"


_SUCCESS = 'SUCCESS'
_ERROR = 'ERROR'


class PageformantException(Exception):
    def __init__(self, *args, **kwargs):
        super(PageformantException, self).__init__(*args, **kwargs)

class PageformantAPI():
    def __init__(self, key, passwd):
        self.apiKey = key
        self.apiPasswd = passwd
        self.lastError = None
        self.enable()

    def sendMessage(self, srvID, message, link, userSpecID = None):
        if not self.is_active():
            self.lastError = PageformantException("Your API-Accessor is currently disabled!")
            return False
        if len(message) > 180:
            self.lastError = PageformantException("Your Message is too long!")
            return False
        # set the parameters
        params = self._getDefaultParams()
        params.update({
            'METHOD':'PostMessage',
            'SERVICEID': str(srvID),
            'MESSAGE': message,
            'LINK': link,
            'USERSPECID':'' })
        if userSpecID:
            params['USERSPECID'] = userSpecID
        self._sendAPIRequest(params)
        return self.lastError == None

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def is_active(self):
        return self.active

    # private methods #
    
    def _getDefaultParams(self):
        return {'APIVERSION': _PF_API_VERSION, 'APIKEY': self.apiKey, 'APIPASSWD': self.apiPasswd }
    
    def _sendAPIRequest(self, params):
        self.lastError = None
        conn = httplib.HTTPConnection(_PF_BASE_URL)
        conn.request("POST", _PF_API_URL, urllib.urlencode(params), {"Content-type": "application/x-www-form-urlencoded"})
        self._handleResponse(conn.getresponse().read())

    def _handleResponse(self, response):
        respAsDict = urlparse.parse_qs(response)
        def getFromDict(aDict, key, defaultValue = ''):
            value = aDict.get(key, defaultValue)
            if type(value) == list:
                return value[0]
            return value
        successOrError = getFromDict(respAsDict, 'ACK')
        if successOrError != _SUCCESS:
            errStr = getFromDict(respAsDict, 'ERRSTR', "No error found in the response!")
            self.lastError = PageformantException("API-Error: %s" %(errStr))
