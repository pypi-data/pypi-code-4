import requests


class Client(object):

    def __init__(self, host="localhost", port=17500):
        self.host = host
        self.port = port
        self.session = requests.session()

    def schedule(self, routing_key, body, interval):
        url = "http://%s:%i/schedule" % (self.host, self.port)
        data = {"routing_key": routing_key, "body": body, "interval": interval}
        response = self.session.post(url, data=data)
        assert response.ok

    def cancel(self, routing_key, body):
        url = "http://%s:%i/cancel" % (self.host, self.port)
        data = {"routing_key": routing_key, "body": body}
        response = self.session.post(url, data=data)
        assert response.ok
