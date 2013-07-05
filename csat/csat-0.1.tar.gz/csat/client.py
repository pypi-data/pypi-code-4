import json
import socket


class Function(object):
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name

    def __call__(self, *args):
        return self.proxy.call(self.name, *args)


class RemoteJsonError(RuntimeError):
    pass


class CouldNotConnect(RuntimeError):
    pass


class JsonRPCProxy(object):

    def __init__(self, host, port):
        self.endpoint = host, port
        self.request_id = 0
        self.socket = None

    def __getattr__(self, name):
        return Function(self, name)

    def call(self, name, *args):
        request_id, self.request_id = self.request_id, self.request_id + 1
        payload = {
            'method': name,
            'params': args,
            'id': request_id,
        }
        self._send_json(payload)
        response = self._recv_json()

        assert request_id == response['id']
        try:
            return response['result']
        except KeyError:
            raise RemoteJsonError('Remote JSON error: {}'.format(
                response['error']['code']))

    def _send_json(self, payload):
        payload = json.dumps(payload)
        self._send_netstring(payload)

    def _send_netstring(self, payload):
        payload = '{}:{},'.format(len(payload), payload)
        self._send(payload)

    def _send(self, payload):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.endpoint)
            except socket.error:
                raise CouldNotConnect()
        self.socket.send(payload)

    def _recv_json(self):
        return json.loads(self._recv_netstring())

    def _recv_netstring(self):
        data = ''

        while ':' not in data:
            data += self._recv(1)

        l = int(data[:-1])
        payload = self._recv(l)
        assert self._recv(1) == ','
        return payload

    def _recv(self, length):
        return self.socket.recv(length)


if __name__ == '__main__':
    proxy = JsonRPCProxy('localhost', 7001)
    print proxy.echo('hello', 1)
