import rsa


class Key(object):

    def __init__(self, data=None, filename=None):
        if data and not filename:
            self.private = self._from_data(data)

        elif filename and not data:
            self.private = self._from_file(filename)

        else:
            raise Exception('must pass data for filename.')

    def _from_data(self, data):
        return rsa.PrivateKey.load_pkcs1(data)

    def _from_file(self, filename):
        with open(filename, 'r') as keyfile:
            keydata = keyfile.read()
        return self._from_data(keydata)
