#! /usr/bin/env python

from Crypto.PublicKey import RSA
from pkg import *
import commons
"""import flask"""
from os import path
from flask import Flask


app = Flask(__name__)
key_file_path = 'pkg_key.pem'

class PkgServer(Pkg):

    instance = None

    def __init__(self, rsa):
        Pkg.__init__(self, rsa)
        print("Init Server")

@app.route('/public_key')
def public_key():
    """
    Returns the Public Master Key of the PKG
    """
    print("Public Key")
    return PkgServer.instance.public_key

@app.route('/gen_public_key/<identity>')
def gen_public_key(identity):
    """
    Returns the Public Key of an individual represented by 'identity'.
    This is an outsourcing service function as it is also available for the
    Client implementation. Should be used if the device running the Client
    application wants to outsource Memory or CPU usage.
    """
    return commons.gen_public_key(identity, PkgServer.instance.public_key)

@app.route('/extract_key/<identity>')
def extract_key(identity):
    """
    Returns the Secret Key of an individual represented by 'identity'.
    The individual must be authenticated before calling this function
    in order not to compromise its Secret Key.
    """
    return PkgServer.instance.extract_key(identity)


if __name__ == "__main__":
    if path.exists(key_file_path):
        with open(key_file_path) as key_file:
            PkgServer.instance = PkgServer(RSA.importKey(key_file.read()))
    else:
        rsa = RSA.generate(2048)
        PkgServer.instance = PkgServer(rsa)
        with open(key_file_path, 'wb') as key_file:
            key_file.write(rsa.exportKey('PEM'))

    app.run(debug=True)
