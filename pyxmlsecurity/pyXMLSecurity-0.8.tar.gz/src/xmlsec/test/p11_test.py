"""
Testing the PKCS#11 shim layer
"""
import xmlsec
import pkg_resources
import unittest

from PyKCS11 import PyKCS11Error
from PyKCS11.LowLevel import CKR_PIN_INCORRECT
from xmlsec.test.case import XMLTestData, load_test_data

__author__ = 'leifj'

import logging,traceback,os,subprocess,unittest,tempfile
from StringIO import StringIO

def _find_alts(alts):
    for a in alts:
        if os.path.exists(a):
            return a
    return None

P11_MODULES = ['/usr/lib/libsofthsm.so','/usr/lib/softhsm/libsofthsm.so']
P11_MODULE = _find_alts(P11_MODULES)
P11_ENGINE = '/usr/lib/engines/engine_pkcs11.so'
P11_SPY = '/usr/lib/pkcs11/pkcs11-spy.so'

try:
    import xmlsec.pk11 as pk11
except Exception:
    pass # catch you later

p11_test_files = []
softhsm_conf = None
global configured
configured = False
server_cert_pem = None
server_cert_der = None
softhsm_db = None

def _tf():
    f = tempfile.NamedTemporaryFile(delete=False)
    p11_test_files.append(f.name)
    return f.name

def _p(args):
    env = {}
    if softhsm_conf is not None:
        env['SOFTHSM_CONF']  = softhsm_conf
    #print "env SOFTHSM_CONF=%s " % softhsm_conf +" ".join(args)
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    out,err = proc.communicate()
    if err is not None and len(err) > 0:
        logging.error(err)
    if out is not None and len(out) > 0:
        logging.debug(out)
    rv = proc.wait()
    if rv:
        raise RuntimeError("command exited with code != 0: %d" % rv)

def setup():
    logging.debug("Creating test pkcs11 token using softhsm")
    try:
        import xmlsec.pk11 as pk11
        global softhsm_conf
        softhsm_db = _tf()
        softhsm_conf = _tf()
        logging.debug("Generating softhsm.conf")
        with open(softhsm_conf,"w") as f:
            f.write("#Generated by pyXMLSecurity test\n0:%s\n" % softhsm_db)
        logging.debug("Initializing the token")
        _p(['softhsm',
            '--slot','0',
            '--label','test',
            '--init-token',
            '--pin','secret1',
            '--so-pin','secret2'])
        logging.debug("Generating 1024 bit RSA key in token")
        _p(['pkcs11-tool',
            '--module', P11_MODULE,
            '-l',
            '-k',
            '--key-type','rsa:1024',
            '--slot','0',
            '--id','a1b2',
            '--label','test',
            '--pin','secret1'])
	_p(['pkcs11-tool',
            '--module', P11_MODULE,
            '-l',
            '--pin','secret1','-O'])
        global signer_cert_der
        global signer_cert_pem
        signer_cert_pem = _tf()
        openssl_conf = _tf()
        logging.debug("Generating OpenSSL config")
        with open(openssl_conf,"w") as f:
            f.write("""
openssl_conf = openssl_def

[openssl_def]
engines = engine_section

[engine_section]
pkcs11 = pkcs11_section

[pkcs11_section]
engine_id = pkcs11
dynamic_path = %s
MODULE_PATH = %s
PIN = secret1
init = 0

[req]
distinguished_name = req_distinguished_name

[req_distinguished_name]
                """ % (P11_ENGINE,P11_MODULE))

        signer_cert_der = _tf()

        logging.debug("Generating self-signed certificate")
        _p(['openssl','req',
            '-new',
            '-x509',
            '-subj',"/cn=Test Signer",
            '-engine','pkcs11',
            '-config', openssl_conf,
            '-keyform','engine',
            '-key','a1b2',
            '-passin','pass:secret1',
            '-out',signer_cert_pem])

        _p(['openssl','x509',
            '-inform','PEM',
            '-outform','DER',
            '-in',signer_cert_pem,
            '-out',signer_cert_der
        ])

        logging.debug("Importing certificate into token")

        _p(['pkcs11-tool',
            '--module',P11_MODULE,
            '-l',
            '--slot','0',
            '--id','a1b2',
            '--label','test',
            '-y','cert',
            '-w',signer_cert_der,
            '--pin','secret1'])

        global configured
        configured = True
    except ImportError,ex:
        print "-" * 64
        traceback.print_exc()
        print "-" * 64
        logging.warning("PKCS11 tests disabled: unable to import xmlsec.pk11: %s" % ex)
    except Exception,ex:
        print "-" * 64
        traceback.print_exc()
        print "-" * 64
        logging.warning("PKCS11 tests disabled: unable to initialize test token: %s" % ex)

def teardown(self):
    for o in self.p11_test_files:
        if os.path.exists(o):
            os.unlink(o)
    self.configured = False
    self.p11_test_files = []

def is_configured():
    global configured
    return configured

def _get_all_signatures(t):
    res = []
    for sig in t.findall(".//{%s}Signature" % xmlsec.NS['ds']):
        sv = sig.findtext(".//{%s}SignatureValue" % xmlsec.NS['ds'])
        assert sv is not None
        # base64-dance to normalize newlines
        res.append(sv.decode('base64').encode('base64'))
    return res

class TestPKCS11(unittest.TestCase):

    def setUp(self):
        datadir = pkg_resources.resource_filename(__name__, 'data')
        self.private_keyspec = os.path.join(datadir, 'test.key')
        self.public_keyspec  = os.path.join(datadir, 'test.pem')

        self.cases = load_test_data('data/signverify')

    #@unittest.skipUnless(is_configured(),"PKCS11 unconfigured")
    def test_is_configured(self):
        assert is_configured()

    #@unittest.skipUnless(configured,"PKCS11 unconfigured")
    def test_open_session(self):
        session = None
        try:
            os.environ['SOFTHSM_CONF'] = softhsm_conf
            session = pk11._session(P11_MODULE,0,"secret1")
            assert session is not None
        except Exception,ex:
            traceback.print_exc()
            raise ex
        finally:
            if session is not None:
                pk11._close_session(session)

    #@unittest.skipUnless(configured,"PKCS11 unconfigured")
    def test_open_session_no_pin(self):
        session = None
        try:
            os.environ['SOFTHSM_CONF'] = softhsm_conf
            session = pk11._session(P11_MODULE,0)
            assert session is not None
        except Exception,ex:
            traceback.print_exc()
            raise ex
        finally:
            if session is not None:
                pk11._close_session(session)

    def test_two_sessions(self):
        session1 = None
        session2 = None
        try:
            os.environ['SOFTHSM_CONF'] = softhsm_conf
            session1 = pk11._session(P11_MODULE,0,"secret1")
            session2 = pk11._session(P11_MODULE,0,"secret1")
            assert session1 != session2
            assert session1 is not None
            assert session2 is not None
        except Exception,ex:
            raise ex
        finally:
            if session1 is not None:
                pk11._close_session(session1)
            if session2 is not None:
                pk11._close_session(session2)

    def test_bad_login(self):
        os.environ['SOFTHSM_CONF'] = softhsm_conf
        try:
            session = pk11._session(P11_MODULE,0,"wrong")
            assert False,"We should have failed the last login"
        except PyKCS11Error,ex:
            assert ex.value == CKR_PIN_INCORRECT
            pass

    #@unittest.skipUnless(configured,"PKCS11 unconfigured")
    def test_find_key(self):
        session = None
        try:
            os.environ['SOFTHSM_CONF'] = softhsm_conf
            session = pk11._session(P11_MODULE,0,"secret1")
            key,cert = pk11._find_key(session,"test")
            assert key is not None
            assert cert is not None
            assert cert.strip() == open(signer_cert_pem).read().strip()
        except Exception,ex:
            raise ex
        finally:
            if session is not None:
                pk11._close_session(session)

    #@unittest.skipUnless(configured,"PKCS11 unconfigured")
    def test_SAML_sign_with_pkcs11(self):
        """
        Test signing a SAML assertion using PKCS#11 and then verifying it using plain file.
        """
        case = self.cases['SAML_assertion1']
        print("XML input :\n{}\n\n".format(case.as_buf('in.xml')))

        os.environ['SOFTHSM_CONF'] = softhsm_conf

        signed = xmlsec.sign(case.as_etree('in.xml'),
                             key_spec="pkcs11://%s:0/test?pin=secret1" % (P11_MODULE)
                             )

        # verify signature using the public key
        res = xmlsec.verify(signed,
                            signer_cert_pem,
                            )
        self.assertTrue(res)
