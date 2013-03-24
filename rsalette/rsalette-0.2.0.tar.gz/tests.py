import rsalette
import asn1lette
import subprocess
import json
import os.path

from nose.tools import eq_, raises

keys = [            
        {'e': 'AQAB', 
         'kty': 'RSA', 
         'n': 'tbg-f-iI33OW7Pll0eah8mmAz-5kQWntKRzP3Bd3dB93523t0ZQEhS17wR4TLOgKBGDGhncMvWUH53-pPWxkDanPXpQ53mK4McQfA6PE__XrgUI_DfpuK-46HJecJnyKcghrSUKkKAM9ZU46zVRsmr84t8IKBwRwzdqfOT3UJEbB3ktqw-1UNsz0ZmBAeZXnETbBGwSo3tTeHOVq0E6kYqmlaO0Eu1jfN8mxLhc1x7_9osjsbO0pkJTchdaVBl7MLpmYNfwlh3eAzir__avGXetJa9fpsP2KAG0_6OSlTh2MzwyuTRTqmU0rQQOHscqoM8VubFH5odRcca3lHFFb0Q'}
       ]

pem = b"""

-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEAtbg+f+iI33OW7Pll0eah8mmAz+5kQWntKRzP3Bd3dB93523t0ZQE
hS17wR4TLOgKBGDGhncMvWUH53+pPWxkDanPXpQ53mK4McQfA6PE//XrgUI/Dfpu
K+46HJecJnyKcghrSUKkKAM9ZU46zVRsmr84t8IKBwRwzdqfOT3UJEbB3ktqw+1U
Nsz0ZmBAeZXnETbBGwSo3tTeHOVq0E6kYqmlaO0Eu1jfN8mxLhc1x7/9osjsbO0p
kJTchdaVBl7MLpmYNfwlh3eAzir//avGXetJa9fpsP2KAG0/6OSlTh2MzwyuTRTq
mU0rQQOHscqoM8VubFH5odRcca3lHFFb0QIDAQAB
-----END RSA PUBLIC KEY-----"""

def test_asn1lette():
    pk = rsalette.PublicKey(*asn1lette.parse_pem(iter(pem.splitlines())))
    eq_(pk.to_jwk(), keys[0])

@raises(ValueError)
def test_asn1lette_fail():
    asn1lette.parse_der(bytearray(b'\x32'))

def test_rsalette():
    in_jwk = keys[0]
    pk = rsalette.PublicKey.from_jwk(in_jwk)
    jwk = pk.to_jwk()
    for param in ('kty', 'n', 'e'):
        eq_(jwk[param], in_jwk[param])
    
    assert 'PublicKey(' in repr(pk)
   
@raises(ValueError)
def test_bad_key():
    rsalette.PublicKey.from_jwk({'kty':'ARS'})

# Generating a suitable keypair:
#
# openssl genrsa -out test_private.pem 2048
# (the python-rsa library was used to extract the public key)

def test_signature():
    for digest in 'sha256', 'sha384', 'sha512':
        _test_signature(digest)
        
def sign_with_openssl(message, key_filename, digest='sha256'):
    """Sign message with openssl, returning the signature.
    
    message: the message in bytes
    key_filename: path to a PEM-format RSA private key
    digest: digest algorithm (see 'openssl dgst' for legal values)
    """
    command = ['openssl', 'dgst', '-' + digest, '-sign', key_filename, '-binary']
    openssl = subprocess.Popen(command, 
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = openssl.communicate(message)
    rc = openssl.wait()
    if rc != 0:
        raise subprocess.CalledProcessError(rc, ' '.join(command), output[1])
    return output[0]

def _test_signature(digest='sha256'):
    our_pubkey = rsalette.PublicKey.from_jwk(keys[0])
    here = os.path.abspath(os.path.dirname(__file__))
    
    message = json.dumps(keys[0]).encode('utf-8')
    signature = sign_with_openssl(message, os.path.join(here, 'test_private.pem'), digest)
    
    verified_message = our_pubkey.verify(message, signature)
    eq_(verified_message, message)
    
    @raises(ValueError)
    def bad_signature():
        our_pubkey.verify(message+b' ', signature)
        
    bad_signature()
