import urllib2
import json
import httplib
from errors import CouchDBOff


def comprobar(host, port):
    try:
        try_conectar = httplib.HTTPConnection(host, str(port))
        try_conectar.connect()
    except Exception, err:
        raise CouchDBOff(err, "You must turn on the CouchDB Server or verify if the host and port are the same where you server is on", 'FAIL')


def send(options, data, cb=""):
    try:
        if type(data).__name__ == "function":
            cb = data
            data = None
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        results = dict()
        url = "http://%s:%s" % (options['host'], str(options['port']))
        url += "%s" % options['path']
        if data is not None:
            request = urllib2.Request(url, data=json.dumps(data))
        else:
            request = urllib2.Request(url)
        request.add_header("Content-Type", "application/json")
        if 'headers' in options:
            for header in options['headers']:
                request.add_header(header, options['headers'][header])
        request.get_method = lambda: options['method'].upper()
        content = opener.open(request)
        for_design = ""
        try:
            for get_json in content:
                    results.update(json.loads(get_json))
        except:
            des = urllib2.urlopen(url)
            try:
                for content in des:
                    for_design += content
                results.update(json.loads(for_design))
            except:
                results = json.loads(content)
        cb(results)
        return results
    except Exception as err:
        raise CouchDBOff(err, "WTF", 'WARNING')

# options = {"host": 'localhost', "port": 5984, "path": '/hello-world', "method": "POST"}
# data = json.dumps({'item': 'melon'})
#def cb(p):
#    print p
#send(options, data, cb)
