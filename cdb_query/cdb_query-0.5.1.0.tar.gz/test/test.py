
url_name='http://esg.cnrm-game-meteo.fr/thredds/fileServer/esg_dataroot1/CMIP5/output1/CNRM-CERFACS/CNRM-CM5/rcp45/mon/atmos/Amon/r1i1p1/v20111006/pr/pr_Amon_CNRM-CM5_rcp45_r1i1p1_200601-205512.nc'



import urllib2, httplib
from cookielib import CookieJar

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

cj = CookieJar()
opener = urllib2.build_opener(HTTPSClientAuthHandler('/home/laliberte/.esg/credentials.pem', '/home/laliberte/.esg/credentials.pem'),urllib2.HTTPCookieProcessor(cj))

response = opener.open(url_name)
print dir(response)
print response.msg
print response.headers.getheaders('Content-Length')[0]
print lengths
print response.getcode()
