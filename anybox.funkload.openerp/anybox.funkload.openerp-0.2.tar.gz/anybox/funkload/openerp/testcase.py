import os
import simplejson as json
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import xmlrpc_get_credential as get_credential
from funkload.utils import xmlrpc_list_credentials
from funkload.utils import Data


class XmlModelProxy(object):
    """An XML-RPC proxy to an OpenObject model class, for Funkload case.

    Inspired from Openobject-library
    """

    def __init__(self, testcase, model):
        self._model = model
        self.url = testcase.server_url + '/xmlrpc/object'
        self.model = model
        self.testcase = testcase

    def __getattr__(self, meth):
        """Return a wrapper method ready for Funkload's xmlrpc calls."""

        def proxy(*args, **kw):
            # exception handling is done by Funkload (logs errors etc)
            tc = self.testcase
            description = kw.pop('description', None)
            return tc.xmlrpc(self.url, 'execute_kw',
                             params=(tc.db_name, tc.uid, tc.pwd,
                                     self.model, meth, args, kw),
                             description=description)
        return proxy

    def workflow(self, action):
        """Return a wrapper method ready to send wkf signals for an object id.
        """
        def proxy(oid, **kw):
            # exception handling is done by Funkload (logs errors etc)
            tc = self.testcase
            description = kw.pop('description', None)
            return tc.xmlrpc(self.url, 'exec_workflow',
                             (tc.db_name, tc.uid, tc.pwd,
                              self.model, action, oid),
                             description=description)
        return proxy


class JsonRpcError(RuntimeError):

    def __init__(self, url, error):
        self.server_error = error
        self.url = url

    def __str__(self):
        return self.url

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.url, self.server_error)


class JsonModelProxy(object):

    def __init__(self, testcase, model):
        self._model = model
        self.url = testcase.server_url
        self.model = model
        self.testcase = testcase

    def search_read(self, domain, fields, description=None):
        tc = self.testcase
        return tc.jsonrpc(self.url + '/web/dataset/search_read',
                          dict(model=self._model,
                               domain=domain,
                               fields=fields,
                               session_id=tc.web_session_id),
                          description=description)

    def __getattr__(self, meth):
        """Return a wrapper method ready for Funkload's xmlrpc calls."""

        def proxy(*args, **kw):
            # exception handling is done by Funkload (logs errors etc)
            tc = self.testcase
            description = kw.pop('description', None)
            return tc.jsonrpc(self.url + '/web/dataset/call_kw',
                              dict(model=self.model,
                                   session_id=tc.web_session_id,
                                   method=meth,
                                   args=args,
                                   kwargs=kw),
                              description=description)
        return proxy

MODEL_RPC = dict(xml=XmlModelProxy,
                 json=JsonModelProxy)


class OpenERPTestCase(FunkLoadTestCase):
    """Base test case class for OpenERP.


    This base test case provides helper methods for OpenERP.

    * API calls: use the ``model()`` method to get an insntance of ModelProxy,
      on which you can execute any ORM method. For instance, to list the ids
      of all customers:

         res_partner = self.model('res.partner')
         res_partner.model.search([('customer', '=', 'True')])

      The ModelProxy also provides the ``workflo object

    * Basic user handling : ``login()`` and ``ensure_user()`` (creation if
      needed of an user having prescribed groups.

    * User handling through credential server: ``login_as_group`` to login
      with an user having the prescribed group from a credential server (see
      Funkload documentation)

    In this TestCase, groups are specified with the fully qualified refence
    from ``ir.model.data``, e.g, ``base.group_sale_manager``.
    """

    def setUp(self):
        self.server_url = self.conf_get('main', 'url')
        self.db_name = self.conf_get('main', 'db_name')
        if self.db_name.startswith('$'):
            self.db_name = os.environ[self.db_name[1:]]

        self.cred_host = self.conf_get('credential', 'host')
        self.cred_port = self.conf_get('credential', 'port')
        self.uid = None
        self.json_counter = 0
        self.web_session_id = ""

    def jsonrpc(self, url, params, description=None):
        self.json_counter += 1
        response = self.post(url, Data('application/json',
                                       json.dumps(dict(jsonrpc="2.0",
                                                       method="call",
                                                       params=params,
                                                       session_id=self.web_session_id,
                                                       id='r' + str(self.json_counter),
                                                       ))),
                             description=description)
        response = json.loads(response.body)
        if 'error' in response:
            raise JsonRpcError(url, response['error'])

        return response['result']

    def model(self, model, rpc='xml'):
        return MODEL_RPC[rpc](self, model)

    def login(self, name, password):
        """Return database user_id."""
        self.uid = self.xmlrpc(self.server_url + '/xmlrpc/common', 'login', (
            self.db_name, name, password))
        self.pwd = password
        return self.uid

    def web_login(self, login, password, description=None):
        """Return session id."""
        result = self.jsonrpc(self.server_url + '/web/session/authenticate',
                              dict(base_location=self.server_url,
                                   db=self.db_name,
                                   login=login,
                                   password=password,
                                   ),
                              description=description)
        self.web_session_id = sid = result['session_id']
        return sid

    def dotted_ref(self, dotted_id):
        return self.model('ir.model.data').get_object_reference(dotted_id)

    def ref(self, model, module, name):
        """Look for model records defined in given module with given name."""
        imd = self.model('ir.model.data')
        ids = imd.search(['&', ('model', '=', model),
                          ('name', '=', name),
                          ('module', '=', module)],
                         description="ir.model.data reference lookup")
        self.assertEquals(len(ids), 1)
        return imd.read(ids, ('res_id',))[0]['res_id']

    def login_as_group(self, group):
        """Uses the credential server to log in with an user of given group.

        Selection depends on the credential server policy (e.g, random).
        """
        login, pwd = get_credential(self.cred_host, self.cred_port, group)
        self.login(login, pwd)

    def ensure_user(self, login, pwd, groups):
        """Create or update user with given groups and password."""
        res_users = self.model('res.users')
        res = res_users.search([('name', '=', login)],
                               description="Search user by login")

        # 4 is the correct value to add to many2many
        group_upd = [(4, self.ref('res.groups', *gr.split('.', 1)))
                     for gr in groups]

        if res:
            self.assertEquals(len(res), 1)
            res_users.write(res, dict(groups_id=group_upd))
        else:
            res_users.create(dict(login=login, password=pwd, name=login,
                                  groups_id=group_upd))

    def ensure_credential_server_users(self):
        """Ensure that users listed in the credential server do exist."""

        users = {}
        for group in ('base.group_sale_manager',):
            for login, pwd in xmlrpc_list_credentials(
                    self.cred_host, self.cred_port, group):
                user = users.setdefault(login, dict(pwd=pwd))
                user.setdefault('groups', set()).add(group)

        for login, info in users.items():
                print login, info
                self.ensure_user(login, info['pwd'], info['groups'])
