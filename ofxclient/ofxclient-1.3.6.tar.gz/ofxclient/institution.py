import StringIO
import hashlib
from ofxclient.client import Client
from ofxparse import OfxParser
from BeautifulSoup import BeautifulStoneSoup

class Institution(object):
    """Represents an institution or bank

    :param id: FI Id
    :type id: string
    :param org: FI Org
    :type org: string
    :param url: FI Url
    :type url: string
    :param username: Customer username or member id
    :type username: string
    :param password: Customer password or PIN
    :type password:
    :param broker_id: FI Broker ID (optional)
    :type broker_id: string
    :param description: Description of the bank (optional)
    :type description: string or None
    :param client_args: connection/application information override (optional)
    :type client_args: kwargs for :py:class:`ofxclient.Client`

    Values for many of the parameters need to come from some sort of
    OFX registry which knows about each banks particular setup.

    For help obtaining this sort of information; please see the
    :py:mod:`ofxhome` python module and/or the `OFX Home <http://ofxhome.com>`_
    website.
    """
    def __init__(self, id, org, url, username, password, broker_id='', description=None, client_args={} ):
        self.id = id
        self.org = org
        self.url = url
        self.broker_id = broker_id
        self.username = username
        self.password = password
        self.description = description or self._default_description()
        self.client_args = client_args

    def client(self):
        """Build a :py:class:`ofxclient.Client` for talking with the bank

        It implicitly passes in the ``self.client_args`` that were passed
        when instantiating this ``Institution``.

        :rtype: :py:class:`ofxclient.Client`
        """
        settings = self.client_args
        return Client(institution=self,**settings)

    def local_id(self):
        """Locally generated unique account identifier.

        :rtype: string
        """
        return hashlib.sha256("%s%s" % (
                self.id,
                self.username )).hexdigest()

    def _default_description(self):
        return self.org

    def authenticate(self,username=None,password=None):
        """Test the authentication credentials

        Raises a ``ValueError`` if there is a problem authenticating
        with the human readable reason given by the institution.

        :param username: optional username (use self.username by default)
        :type username: string or None
        :param password: optional password (use self.password by default)
        :type password: string or None
        """

        u = username or self.username
        p = password or self.password

        client = self.client()
        query  = client.authenticated_query(username=u,password=p)
        res    = client.post(query)
        ofx    = BeautifulStoneSoup(res)

        sonrs = ofx.find('sonrs')
        code = int(sonrs.find('code').contents[0].strip())

        try:
            status = sonrs.find('message').contents[0].strip()
        except Exception:
            status = ''

        if code == 0:
            return 1

        raise ValueError(status)

    def accounts(self):
        """Ask the bank for the known :py:class:`ofxclient.Account` list.
        
        :rtype: list of :py:class:`ofxclient.Account` objects
        """
        from ofxclient.account import Account
        client  = self.client()
        query   = client.account_list_query()
        resp    = client.post(query)
        resp_handle = StringIO.StringIO(resp)

        accounts = []

        for a in OfxParser.parse(resp_handle).accounts:
            accounts.append( Account.from_ofxparse(a,institution=self) )
        return accounts

    def serialize(self):
        """Serialize predictably for use in configuration storage.

        Output looks like this::

          {
            'local_id':    'unique local identifier',
            'id':          'FI Id',
            'org':         'FI Org',
            'url':         'FI OFX Endpoint Url',
            'broker_id':   'FI Broker Id',
            'username':    'Customer username',
            'password':    'Customer password',
            'description': 'descr',
            'client_args': {
                'id':          'random client id - see Client() for default',
                'app_id':      'app name - see Client() for default',
                'app_version': 'app version - see Client() for default',
                'ofx_version': 'ofx version - see Client() for default',
            }
          }

        :rtype: nested dictionary
        """
        client = self.client()
        client_args = {
                'id': client.id,
                'app_id': client.app_id,
                'app_version': client.app_version,
                'ofx_version': client.ofx_version,
        }
        return {
                'id': self.id,
                'org': self.org,
                'url': self.url,
                'broker_id': self.broker_id,
                'username': self.username,
                'password': self.password,
                'description': self.description,
                'client_args': client_args,
                'local_id': self.local_id()
        }

    @staticmethod
    def deserialize(raw):
        """Instantiate :py:class:`ofxclient.Institution` from dictionary

        :param raw: serialized ``Institution``
        :param type: dict as given by :py:method:`~ofxclient.Institution.serialize`
        :rtype: subclass of :py:class:`ofxclient.Institution`
        """
        return Institution(
                id = raw['id'],
                org = raw['org'],
                url = raw['url'],
                broker_id = raw.get('broker_id',''),
                username = raw['username'],
                password = raw['password'],
                description = raw.get('description',None),
                client_args = raw.get('client_args',{}),
        )
