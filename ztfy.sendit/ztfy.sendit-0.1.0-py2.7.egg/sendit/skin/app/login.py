### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages
from datetime import datetime
from httplib import UNAUTHORIZED

# import Zope3 interfaces
from z3c.form.interfaces import HIDDEN_MODE, IErrorViewSnippet
from zope.authentication.interfaces import IAuthentication
from zope.component.interfaces import ISite
from zope.pluggableauth.interfaces import IAuthenticatedPrincipalCreated
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.security.interfaces import IUnauthorized

# import local interfaces
from ztfy.appskin.interfaces import IAnonymousPage
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.user.interfaces import ISenditApplicationUsers
from ztfy.skin.interfaces import IDefaultView

# import Zope3 packages
from z3c.form import field, button
from zope.component import adapter, queryMultiAdapter, getMultiAdapter, queryUtility, getUtilitiesFor
from zope.interface import implements, Interface, Invalid
from zope.publisher.skinnable import applySkin
from zope.schema import TextLine, Password
from zope.site import hooks
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.skin.form import BaseAddForm
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        description=_("Principal ID or email address"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        required=True)

    came_from = TextLine(title=_("camefrom-field", "Login origin"),
                         required=False)


def canRegister(form):
    context = form.context
    app = getParent(context, ISenditApplication)
    return (app is not None) and app.open_registration


class LoginView(BaseAddForm):
    """Main login view"""

    implements(IAnonymousPage)

    legend = _("Please entel valid credentials to login")
    css_class = 'login_view'
    icon_class = 'icon-lock'

    fields = field.Fields(ILoginFormFields)

    def __call__(self):
        self.request.response.setStatus(UNAUTHORIZED)
        return super(LoginView, self).__call__()

    @property
    def action(self):
        if IUnauthorized.providedBy(self.context):
            context, _action, _permission = self.context.args
        else:
            context = self.context
        app = getParent(context, ISenditApplication)
        return '%s/@@login.html' % absoluteURL(app, self.request)

    @property
    def help(self):
        profile = IProfile(self.request.principal, None)
        if (profile is not None) and profile.disabled:
            return _("This account is disabled. Please login with an enabled account or contact the administrator.")
        if canRegister(self):
            return _("Please enter login credentials or click 'Register' button to request a new account")

    def updateWidgets(self):
        super(LoginView, self).updateWidgets()
        self.widgets['came_from'].mode = HIDDEN_MODE
        self.widgets['came_from'].value = self.request.get('came_from') or self.request.get('PATH_INFO')

    def updateActions(self):
        super(LoginView, self).updateActions()
        self.actions['login'].addClass('btn')
        if canRegister(self):
            self.actions['register'].addClass('btn btn-warning')

    def extractData(self, setErrors=True):
        data, errors = super(LoginView, self).extractData(setErrors=setErrors)
        if errors:
            return data, errors
        self.request.form['login'] = data['username']
        self.request.form['password'] = data['password']
        self.principal = None
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    try:
                        self.principal = auth.authenticate(self.request)
                        if self.principal is not None:
                            profile = IProfile(self.principal)
                            if not profile.activated:
                                error = Invalid(_("This user profile is not activated. Please check your mailbox to get activation instructions."))
                                view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                                       IErrorViewSnippet)
                                view.update()
                                errors += (view,)
                                if setErrors:
                                    self.widgets.errors = errors
                            return data, errors
                    except:
                        continue
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        if self.principal is None:
            error = Invalid(_("Invalid credentials"))
            view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
            if setErrors:
                self.widgets.errors = errors
        return data, errors

    @button.buttonAndHandler(_("login-button", "Login"), name="login")
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if self.principal is not None:
            app = getParent(self.context, ISenditApplication)
            ISenditApplicationUsers(app).addUserFolder(self.principal)
            if IUnauthorized.providedBy(self.context):
                context, _action, _permission = self.context.args
                self.request.response.redirect(absoluteURL(context, self.request))
            else:
                came_from = data.get('came_from')
                if came_from:
                    self.request.response.redirect(came_from)
                else:
                    target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
                    self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request),
                                                              target.viewname if target is not None else '@@index.html'))
            return ''
        else:
            self.request.response.redirect('%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                             data.get('came_from')))

    @button.buttonAndHandler(_("register-button", "Register"), name="register", condition=canRegister)
    def handleRegister(self, action):
        self.request.response.redirect('%s/@@register.html' % absoluteURL(self.context, self.request))


class LogoutView(BaseAddForm):
    """Main logout view"""

    def __call__(self):
        skin = queryUtility(IBrowserSkinType, self.context.getSkin())
        applySkin(self.request, skin)
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    auth.logout(self.request)
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
        self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request),
                                                  target.viewname if target is not None else '@@SelectedManagementView.html'))
        return ''


@adapter(IAuthenticatedPrincipalCreated)
def handleAuthenticatedPrincipal(event):
    """Handle authenticated principals
    
    Internal principals are automatically activated
    """
    app = getParent(event.authentication, ISenditApplication)
    if app is not None:
        profile = IProfile(event.principal)
        if not profile.activated:
            name, _plugin, _info = profile.getAuthenticatorPlugin()
            if name in app.internal_auth_plugins:
                profile.activation_date = datetime.utcnow()
                profile.activated = True
