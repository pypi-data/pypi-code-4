from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2 import BINDING_PAOS, BINDING_SOAP
from saml2.server import Server
from saml2.client import Saml2Client
from saml2.ecp_client import Client

__author__ = 'rolandh'

_passwd = "foo"

sp = Saml2Client(config_file="servera_conf")
idp = Server(config_file="idp_all_conf")

ecc = Client("", _passwd, xmlsec_binary=sp.config.xmlsec_binary,
             disable_ssl_certificate_validation=True)
ecc.metadata = sp.metadata
ecc.sec = sp.sec

acsus = sp.config.endpoint('assertion_consumer_service', BINDING_PAOS)

binding, destination = sp.pick_binding("single_sign_on_service", [BINDING_SOAP],
                                       entity_id=idp.config.entityid)

request = sp.create_authn_request(destination, sign=False, binding=BINDING_SOAP,
                                  nameid_format=NAMEID_FORMAT_PERSISTENT)

headers = None

# send the request and receive the response
response = ecc.phase2(request, acsus[0], idp.config.entityid, headers,
                      sign=True)

print response