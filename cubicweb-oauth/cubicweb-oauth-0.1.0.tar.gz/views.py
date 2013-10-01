# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-oauth views/forms/actions/components for web ui"""
import urllib

from logilab.common.decorators import clear_cache

from cubicweb.utils import make_uid
from cubicweb.predicates import anonymous_user, configuration_values, match_form_params

from cubicweb.view import View
from cubicweb.web.controller import Controller
from cubicweb.web.views import authentication, urlrewrite, forms
from cubicweb.web.views import basecomponents, basetemplates
from cubicweb.web import Redirect, formfields, formwidgets

from cubicweb.server import Service

from cubes.oauth.authplugin import EXT_TOKEN

_ = unicode

NEGOSTATE = {} # negoid -> service coordinates
COLLECT_LIST = []

LOGINNOWSTATE = {}


def login_now(self, login):
    req = self._cw
    key = make_uid()
    LOGINNOWSTATE[key] = login
    clear_cache(req, 'get_authorization')
    # prepare login info for .set_session call
    req.form['__externalauthlogin'] = login
    req.form['__externalauthkey'] = key
    # close anonymous connection
    if req.cnx:
        req.cnx.close()
    req.cnx = None
    try:
        self.appli.session_handler.set_session(req)
    except Redirect:
        pass
    if not req.user.login == login:
        self.warning('should be now logged as %s, but still %s', login, req.user.login)

class ExternalAuthReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/externalauth-confirm', {'vid':'externalauth-confirm'})
    ]


class ExternalAuthConfirmError(Controller):
    __regid__ = 'externalauth-confirm'
    # XXX check if these error_xxx are parts of oauth1/2
    __select__ = match_form_params(
        'error_code', 'error_message', '__externalauth_negociationid')

    def publish(self, rset=None):
        form = self._cw.form
        raise Redirect(self._cw.build_url(
            __message='error while authenticating: %s %s'
            % (form.get('error_code'), form.get('error_message', ''))))


class ExternalAuthConfirm(Controller):
    __regid__ = 'externalauth-confirm'
    __select__ = match_form_params('code', '__externalauth_negociationid')

    def _nego_timeout_url(self):
        msg = self._cw._('Authentication timeout. Please try again.')
        return self._cw.build_url(__message=msg)

    def publish(self, rset=None):
        form = self._cw.form
        code = form.get('code')
        negociationid = form.get('__externalauth_negociationid')
        if not (code and negociationid):
            return

        nego = NEGOSTATE.pop(negociationid, None)
        if nego is None:
            return Redirect(self._nego_timeout_url())

        with self.appli.repo.internal_session() as session:
            try:
                service = session.entity_from_eid(nego['service'])
                adapter = service.cw_adapt_to('externalauth.service')
                oauth2_session = adapter.oauth2_service.get_auth_session(data={
                    'code': code,
                    'redirect_uri': nego['redirect_uri']
                })

                infos = adapter.provider.retrieve_info(oauth2_session)
                extid_rset = session.execute(
                    'ExternalIdentity SI WHERE SI provider P, '
                    'P eid %(peid)s, SI uid %(uid)s',
                    {'peid': service.provider[0].eid, 'uid': infos['uid']}
                )
                assert extid_rset.rowcount < 2
                if extid_rset:
                    external_identity = extid_rset.get_entity(0, 0)
                else:
                    external_identity = session.create_entity(
                        'ExternalIdentity', provider=service.provider[0],
                        uid=infos['uid']
                    )

                # deactivate any previous access_token
                session.execute(
                    'SET X active FALSE WHERE '
                    'X is OAuth2Session, '
                    'S external_identity SI, SI eid %(sieid)s, '
                    'S service SE, SE eid %(seid)s',
                    {'sieid': external_identity.eid, 'seid': service.eid}
                )
                oauth2_session = session.create_entity(
                    'OAuth2Session', service=service,
                    external_identity=external_identity,
                    access_token=oauth2_session.access_token,
                    active=True
                )

                session.commit(free_cnxset=False)
            except Exception, e:
                raise Redirect(self._cw.build_url(__message=str(e)))

            if external_identity.identity_of:
                user = external_identity.identity_of[0]
                self.debug('identified %s on %s as %s' % (
                    user.login, service.provider[0].name, infos['uid']))
                login_now(self, user.login)
                raise Redirect(self._cw.build_url())
            else:
                self.debug(
                    "Unknown identity %s on %s: will create a local account",
                    infos['uid'], service.provider[0].name)
                token = make_uid()
                infos.update({
                    'external_identity': external_identity,
                    'oauth2_session': oauth2_session
                })
                self._cw.session.data[token] = infos
                raise Redirect(self._cw.build_url(
                    vid='externalauth-createuser',
                    __token=token
                ))


class ExternalAuthCreateUserForm(forms.FieldsForm):
    __regid__ = action = 'externalauth-createuser'

    form_buttons = [
        formwidgets.SubmitButton(label=_('create user')),
        formwidgets.ResetButton(label=_('cancel')),
    ]



class RegisterUserService(Service):
    __regid__ = 'oauth_register_user' # in CW 3.18, use the standard one
    default_groups = ('users',)

    def call(self, login, password, email=None, groups=None, **kwargs):
        session = self._cw
        # for consistency, keep same error as unique check hook (although not required)
        errmsg = session._('the value "%s" is already used, use another one')
        if (session.execute('CWUser X WHERE X login %(login)s', {'login': login},
                            build_descr=False)
            or session.execute('CWUser X WHERE X use_email C, C address %(login)s',
                               {'login': login}, build_descr=False)):
            qname = role_name('login', 'subject')
            raise ValidationError(None, {qname: errmsg % login})
        # we have to create the user
        if isinstance(password, unicode):
            # password should *always* be utf8 encoded
            password = password.encode('UTF8')
        kwargs['login'] = login
        kwargs['upassword'] = password
        user = session.create_entity('CWUser', **kwargs)
        if groups is None:
            groups = self.default_groups
        if groups:
            session.execute('SET X in_group G WHERE X eid %%(x)s, G name IN (%s)' %
                            ','.join(repr(u) for u in groups),
                            {'x': user.eid})
        if email or '@' in login:
            d = {'login': login, 'email': email or login}
            if session.execute('EmailAddress X WHERE X address %(email)s', d,
                               build_descr=False):
                qname = role_name('address', 'subject')
                raise ValidationError(None, {qname: errmsg % d['email']})
            session.execute('INSERT EmailAddress X: X address %(email)s, '
                            'U primary_email X, U use_email X '
                            'WHERE U login %(login)s', d, build_descr=False)
        return True


class ExternalAuthCreateUserController(Controller):
    __regid__ = 'externalauth-createuser'

    def publish(self, rset=None):
        token = self._cw.form.get('__token')
        if not token:
            raise Redirect(self._cw.build_url())
        infos = self._cw.session.data[token]
        if not infos:
            raise Redirect(self._cw.build_url())

        login = self._cw.form.get('identity').strip()
        # make a dumb un-guessable password
        password = make_uid()

        # TODO insert more informations from the external service
        with self.appli.repo.internal_session() as session:
            session.call_service('oauth_register_user',
                                 login=login,
                                 password=password,
                                 email=infos['email'],
                                 firstname=infos['firstname'],
                                 surname=infos['lastname'])

            session.execute(
                'SET X identity_of U '
                'WHERE X is ExternalIdentity, X eid %(sieid)s, '
                'U is CWUser, U login %(login)s',
                {'sieid': infos['external_identity'].eid, 'login': login}
            )
            session.commit()

            login_now(self, login)
            raise Redirect(self._cw.build_url('cwuser/%s?vid=edition' % login))


class ExternalAuthCreateUserFormView(View):
    __regid__ = 'externalauth-createuser'

    def call(self, **kwargs):
        w, _ = self.w, self._cw._
        token = self._cw.form.get('__token')
        if not token:
            raise Redirect(self._cw.build_url())
        infos = self._cw.session.data[token]
        if not infos:
            raise Redirect(self._cw.build_url())

        form = self._cw.vreg['forms'].select('externalauth-createuser', self._cw)
        form.add_hidden('__token', value=token)
        form.append_field(
            formfields.StringField(
                name='identity',
                label=self._cw._('local identity'),
                max_length=254,
                value=infos['username']
            )
        )
        form.render(w=w)


class yes_marker(object):
    def __bool__(self):
        return True

from cubicweb.dbapi import _repo_connect, ConnectionProperties


class ExternalAuthRetrieverStart(authentication.WebAuthInfoRetreiver):
    """External authentication first step.

    Will only redirect on the demanded service.
    """
    __regid__ = 'externalauth-authenticate-start'
    order = 9

    def _base_url(self):
        # NOTE self._cw is the registry !
        return self._cw.config['base-url']

    def _build_url(self, vid='view', **kwargs):
        base_url = self._base_url()
        # TODO some escaping is missing here, see if we can use urllib helpers
        urlargs = urllib.urlencode(kwargs)
        if urlargs:
            return '%s%s?%s' % (base_url, vid, urlargs)
        return '%s%s' % (base_url, vid)

    def request_has_auth_info(self, req):
        return '__externalauthprovider' in req.form

    def revalidate_login(self, req):
        # TODO I don't understand why this method is needed
        return yes_marker()

    def authentication_information(self, req):
        providername = req.form.get('__externalauthprovider')
        if providername is None:
            raise authentication.NoAuthInfo

        self.info(
            'external authenticator (%s) building auth info %s',
            self.__class__.__name__, req.form
        )

        vreg = self._cw  # YES, see cw/web/views/authentication.py ~106
        repo = vreg.config.repository(vreg)
        with repo.internal_session() as session:

            servicerset = session.execute(
                'ExternalAuthService S WHERE S provider P, P spid %(spid)s',
                {'spid': providername}
            )
            if not servicerset:
                self.error('no service for provider: %s' % providername)
                raise Redirect(self._build_url(
                    __message='no service for provider %s' % providername
                ))

            service = servicerset.get_entity(0, 0)

            negoid = make_uid('nego')
            nego = {'service': service.eid,
                    'redirect_uri': self._build_url(
                        'externalauth-confirm',
                        __externalauth_negociationid=negoid
                    )}
            NEGOSTATE[negoid] = nego
            service_adapter = service.cw_adapt_to('externalauth.service')
            url = service_adapter.oauth2_service.get_authorize_url(
                redirect_uri=nego['redirect_uri'],
                scope=service_adapter.provider.scope
            )
            raise Redirect(url)


class ExternalAuthRetrieverFinish(authentication.WebAuthInfoRetreiver):
    __regid__ = 'externalauth-authenticate-finish'
    order = ExternalAuthRetrieverStart.order - 1

    def request_has_auth_info(self, req):
        # self.info('%s: Checking %s' % (self.__class__.__name__, req))
        login = LOGINNOWSTATE.get(req.form.get('__externalauthkey'), None)
        return ('__externalauthlogin' in req.form and
                '__externalauthkey' in req.form and
                login == req.form['__externalauthlogin'])

    def revalidate_login(self, req):
        if self.request_has_auth_info(req):
            return req.form.get('__externalauthlogin')

    def authentication_information(self, req):
        if not self.request_has_auth_info(req):
            raise authentication.NoAuthInfo

        self.info('external authenticator (%s) building auth info %s',
                  self.__class__.__name__, req.form)

        del LOGINNOWSTATE[req.form.get('__externalauthkey')]
        login = req.form['__externalauthlogin']

        self.info('Identifying %s', login)

        return login, {'__externalauth_directauth': EXT_TOKEN}


# form, link and view

class ExternalAuthLogForm(basetemplates.BaseLogForm):
    __regid__ = domid = 'externalauthlogform'
    boxid = 'externalauthlogbox'

    __externalauthprovider = formfields.StringField(
        '__externalauthprovider', label=_('externalauthprovider'),
        widget=formwidgets.TextInput({'class': 'data'}),
        # NOTE: could be a dropdown with a pre-cooked list ...
        value='facebook'
    )

    onclick_args = ('externalauthlogbox', '__externalauthprovider')


class ExternalAuthLoginLink(basecomponents.HeaderComponent):
    __regid__ = 'externalauthlink'
    __select__ = (
        basecomponents.HeaderComponent.__select__ and
        configuration_values('auth-mode', 'cookie') &
        anonymous_user()
    )

    context = _('header-right')
    onclick = "javascript: cw.htmlhelpers.popupLoginBox('%s', '%s');"

    def render(self, w):
        text = self._cw._('external auth login')
        w(u"""<a href="#" onclick="%s">%s</a>""" % (
            self.onclick % ('externalauthlogbox', '__externalauthprovider'),
            text
        ))
        self._cw.view(
            'externalauthlogform', rset=self.cw_rset,
            id='externalauthlogbox', w=w
        )


class ExternalAuthLogFormView(View):
    __regid__ = 'externalauthlogform'
    __select__ = configuration_values('auth-mode', 'cookie')

    help_msg = _("""
Select the provider you want to use to authenticate.
    """)

    title = _('log in using a provider')

    def call(self, id='externalauthlogbox'):
        w = self.w

        w(u'<div id="%s" class="popupLoginBox hidden">' % id)
        w(u'<p>%s</p>' % self._cw._(self.help_msg))
        form = self._cw.vreg['forms'].select('externalauthlogform', self._cw)
        form.render(w=w)
        w(u'</div>')
