from Crypto.Hash import SHA256
from commons import *
import requests

class Client(object):
    """
    Client contains all the basic functions of a client perspective
    of an IBE scheme. Client will have its own Secret Key and the PKG
    Master Public Key. This way it can calculate any Public Key, 
    including its own.
    """
    
    def __init__(self, identity, pkg_url):
        self.identity = identity
        self.pkg_url = pkg_url
        self.pkg_public_key = requests.get(self.pkg_url + '/public_key/').text

        self.public_key = gen_public_key(self.identity, self.pkg_public_key)
        #TODO authenticate with server 
        self.private_key = requests.get(self.pkg_url + '/extract_key/' + self.identity).text

if __name__ == '__main__':
    client = Client('foo@example.com', 'http://localhost:5000')
    print(client.public_key)
    print(client.private_key)
