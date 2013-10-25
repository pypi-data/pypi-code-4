import json
import urllib2
import base64
import xmlrpclib


class BaseChecker(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.is_valid = False
        self.check()

    def check(self):
        raise NotImplementedError

    def to_python(self):
        return {
            "url": self.url,
            "name": self.name,
            "is_valid": self.is_valid
        }

    def to_json(self):
        json.dumps(self.to_python())


class URLChecker(BaseChecker):
    def __init__(self, *args, **kwargs):
        self.http_user = kwargs.pop('http_user', None)
        self.http_password = kwargs.pop('http_password', None)
        super(URLChecker, self).__init__(*args, **kwargs)

    def open_url(self, url):
        request = urllib2.Request(url)
        if self.http_user and self.http_password:
            base64string = base64.encodestring('%s:%s' % (self.http_user, self.http_password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
        try:
            result = urllib2.urlopen(request)
        except urllib2.URLError:
            self.is_valid = False
            return None
        return result

    def check(self):
        content = self.open_url(self.url)
        if content is not None:
            self.is_valid = content.getcode() == 200
        else:
            self.is_valid = False
        return self.is_valid


class JenkinsChecker(URLChecker):
    """
    You must provide the "lastCompletedBuild" API link as json
    in the __init__

    For example :
    chk = JenkinsChecker(name="MyJenkinsJob", url="http://ci.mydomain.com/", jenkins_url="http://ci.mydomain.com/job/MyJob/lastCompletedBuild/api/json")

    You can also provide "http_user" and "http_password" for auth.
    """
    def __init__(self, *args, **kwargs):
        self.jenkins_url = kwargs.pop('jenkins_url')
        super(JenkinsChecker, self).__init__(*args, **kwargs)

    def check(self):
        content = self.open_url(self.jenkins_url)
        if content is None:
            return False
        datas = json.loads(content.read())
        self.is_valid = datas.get('result', "") == u"SUCCESS"
        return self.is_valid


class SupervisorChecker(BaseChecker):
    """
    You must provide the XMLRPC bind (address + port)
    in the __init__()
    """
    def __init__(self, *args, **kwargs):
        self.bind = kwargs.pop('bind')
        self.process_name = kwargs.pop('process_name')
        super(SupervisorChecker, self).__init__(*args, **kwargs)

    def check(self):
        server = xmlrpclib.ServerProxy('http://%s/RPC2' % self.bind)
        try:
            proc_info = server.supervisor.getProcessInfo(self.process_name)
            self.is_valid = proc_info.get('statename') == 'RUNNING'
        except xmlrpclib.Fault:
            self.is_valid = False
        return self.is_valid
