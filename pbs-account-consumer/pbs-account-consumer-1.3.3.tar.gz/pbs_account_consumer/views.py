import collections
import functools
import urllib
from urlparse import urlsplit, urljoin

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from openid.consumer.consumer import (Consumer, SUCCESS, CANCEL, FAILURE,
                                      SETUP_NEEDED)
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import ax, sreg
from openid.message import NamespaceMap


from .store import DjangoOpenIDStore
from .forms import ChangePasswordForm
from .constants import AX_MAPPINGS, AX_OLDPASSWD, AX_NEWPASSWD, AX_IS_VERIFIED

AXData = collections.namedtuple('AXData', ['ax_alias', 'field_name', 'value'])


def handle_openid_response(func):
    @functools.wraps(func)
    def wrapper(request, redirect_field_name=REDIRECT_FIELD_NAME,
                template_name='openid/response.html'):
        openid_response = parse_openid_response(request)
        if not openid_response:
            return render(
                request, template_name,
                {'message': 'This is an OpenID relying party endpoint.'},
                status=400)

        if openid_response.status == FAILURE:
            message = 'OpenID authentication failed: %s' % openid_response.message
            return render(request, template_name, {'message': message})

        if openid_response.status == CANCEL:
            return render(request, template_name,
                          {'message': 'Authentication cancelled'})

        if openid_response.status == SETUP_NEEDED:
            # setup_needed means the immediate request failed, and we need to
            # redirect the user to either a server side login page
            # (openid_response.setup_url) or a consumer side login page.
            setup_url_param = urllib.urlencode({
                'setup_url': openid_response.setup_url})
            return HttpResponseRedirect(
                "%s?%s" % (reverse('login_setup_needed'), setup_url_param))

        result = func(request, redirect_field_name=redirect_field_name,
                      template_name=template_name,
                      openid_response=openid_response)
        if result is not None:
            return result

        message = 'Unknown OpenID response type: %r' % openid_response.status
        return render(
            request, template_name, {'message': message}, status=400
        )

    return wrapper


def get_sreg_settings():
    return getattr(settings, 'SREG_OPTIONAL', ['email', 'fullname'])


def build_return_to_url(request, return_view, redirect_field_name,
                        redirect_to):
    if hasattr(settings, 'OPENID_CUSTOM_RETURN_TO'):
        return_to = getattr(settings, 'OPENID_CUSTOM_RETURN_TO') + reverse(return_view)
    else:
        return_to = request.build_absolute_uri(reverse(return_view))

    if redirect_to:
        return_to += '&' if '?' in return_to else '?'
        return_to += urllib.urlencode({redirect_field_name: redirect_to})
    return return_to


def _prepare_ax_fetch_request():
    if not any([
            getattr(settings, 'AX_FETCH_IS_VERIFIED', False)]):
        return None

    ax_request = ax.FetchRequest()
    if getattr(settings, 'AX_FETCH_IS_VERIFIED', False):
        ax_request.add(ax.AttrInfo(AX_MAPPINGS[AX_IS_VERIFIED][0], required=True, alias='verified'))

    return ax_request


def login_begin(request, redirect_field_name=REDIRECT_FIELD_NAME,
                template_name='openid/response.html', immediate=False):

    # Set redirect from settings file for immediate redirects.
    # We must set this here for checkid_immediate since the request
    # will be coming from the provider.
    if immediate:
        redirect_to = settings.LOGIN_REDIRECT_URL
    else:
        redirect_to = request.REQUEST.get(redirect_field_name, '')

    openid_url = settings.OPENID_SSO_SERVER_URL

    if openid_url is None:
        return HttpResponseRedirect(redirect_field_name)

    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure, exc:
        return render(
            request, template_name,
            {'message': "OpenID discovery error: %s" % str(exc)}
        )

    sreg_request = sreg.SRegRequest(optional=get_sreg_settings())
    openid_request.addExtension(sreg_request)

    ax_request = _prepare_ax_fetch_request()
    if ax_request:
        openid_request.addExtension(ax_request)

    return_to = build_return_to_url(request, login_complete,
                                    redirect_field_name, redirect_to)
    return render_openid_request(request, openid_request, return_to, immediate)


@handle_openid_response
def login_complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
                   template_name='openid/response.html', openid_response=None):
    if openid_response is None:
        openid_response = parse_openid_response(request)
    if openid_response.status == SUCCESS:
        user = authenticate(openid_response=openid_response)
        if user is None:
            return render(
                request, template_name, {'message': 'Unkown user'}
            )
        if getattr(user, 'requires_verified_email', False):
            return render(
                request, template_name, {'message': 'Verify your email'}
            )
        if not user.is_active:
            return render(
                request, template_name, {'message': 'Disabled account'}
            )
        login(request, user)
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        return HttpResponseRedirect(
            redirect_to=sanitise_redirect_url(redirect_to)
        )


def sanitise_redirect_url(redirect_to):
    # Light security check -- make sure redirect_to isn't garbage.
    is_valid = True
    if not redirect_to or ' ' in redirect_to:
        is_valid = False
    elif '//' in redirect_to:
        # Allow the redirect URL to be external if it's a permitted domain
        allowed_domains = settings.ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS
        _, netloc, _, _, _ = urlsplit(redirect_to)
        # allow it if netloc is blank or if the domain is allowed
        if netloc:
            # a domain was specified. Is it an allowed domain?
            if netloc.find(":") != -1:
                netloc, _ = netloc.split(":", 1)
            if netloc not in allowed_domains:
                is_valid = False

    # If the return_to URL is not valid, use the default.
    if not is_valid:
        redirect_to = settings.LOGIN_REDIRECT_URL

    return redirect_to


def make_consumer(request):
    """Create an OpenID Consumer object for the given Django request."""
    session = request.session.setdefault('OPENID', {})
    store = DjangoOpenIDStore()
    return Consumer(session, store)


def render_openid_request(request, openid_request, return_to, immediate=False,
                          trust_root=None):
    """Render an OpenID authentication request."""
    if trust_root is None:
        trust_root = getattr(
            settings, 'OPENID_CUSTOM_REALM', request.build_absolute_uri('/')
        )

    if openid_request.shouldSendRedirect():
        redirect_url = openid_request.redirectURL(trust_root, return_to, immediate)
        return HttpResponseRedirect(redirect_url)
    else:
        form_html = openid_request.htmlMarkup(
            trust_root, return_to, immediate, form_tag_attrs={'id': 'openid_message'}
        )
        return HttpResponse(form_html, content_type='text/html;charset=UTF-8')


def parse_openid_response(request):
    """Parse an OpenID response from a Django request."""
    if hasattr(settings, 'OPENID_CUSTOM_REALM'):
        current_url = urljoin(getattr(settings, 'OPENID_CUSTOM_REALM'),
                              request.get_full_path())
    else:
        current_url = request.build_absolute_uri()
    consumer = make_consumer(request)
    return consumer.complete(dict(request.REQUEST.items()), current_url)


def setup_needed(request, template_name="openid/setup_needed.html"):
    """
    Render a page in response to openid server returning setup_needed response
    """
    setup_url = request.GET.get('setup_url', '')
    return render(request, template_name, {'setup_url': setup_url})


def reverse_ax_mapper(data):
    ax_mapping = []
    for key, value in data.iteritems():
        try:
            ax_key = AX_MAPPINGS[key][0]
            ax_mapping.append(AXData(ax_key, key, value))
        except (KeyError, IndexError):
            continue
    return ax_mapping


def _make_ax_request(data):
    aliases = NamespaceMap()
    ax_data = reverse_ax_mapper(data)
    for data in ax_data:
        aliases.addAlias(data.ax_alias, data.field_name)
    ax_request = ax.StoreRequest(aliases)
    for data in ax_data:
        ax_request.setValues(data.ax_alias, [data.value])
    return ax_request


@handle_openid_response
def ax_change_complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
                       template_name='openid/response.html',
                       openid_response=None):
    if openid_response is None:
        openid_response = parse_openid_response(request)
    if openid_response.status == SUCCESS:
        ax_response = openid_response.extensionResponse(
            'http://openid.net/srv/ax/1.0', False)
        if ax_response['mode'] == "store_response_success":
            messages.success(request, 'Successfully updated.')
        else:
            messages.error(
                request, ax_response['error'].replace('.*', '.<br/>*'))
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    return HttpResponseRedirect(redirect_to=sanitise_redirect_url(redirect_to))


def ax_update(request, data, redirect_field_name=REDIRECT_FIELD_NAME):
    openid_url = settings.OPENID_SSO_SERVER_URL
    if openid_url is None:
        return HttpResponseRedirect("/")
    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure, exc:
        return HttpResponse("discovery failed %s" % str(exc))
    ax_request = _make_ax_request(data)
    openid_request.addExtension(ax_request)
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    return_to = build_return_to_url(request, ax_change_complete,
                                    redirect_field_name, redirect_to)
    return render_openid_request(request, openid_request, return_to, True)


def _make_password_ax_store(request, old_password, new_password):
    data = {AX_OLDPASSWD: old_password,
            AX_NEWPASSWD: new_password}
    return ax_update(request, data)


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            return _make_password_ax_store(
                request, form.cleaned_data["old_password"],
                form.cleaned_data["new_password"])
    else:
        form = ChangePasswordForm()
    return render(request, "registration/change_password.html",
                  {"form": form})
