import json

from auth_pack.decorators import json_view
from django.conf import settings
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from crispy_forms.utils import render_crispy_form
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth import get_user_model
from auth_pack.forms import UserRegistrationForm, UserAuthenticationForm, UserChangePasswordForm, GenericSetPasswordForm, GenericPassowrdResetForm
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.http import HttpResponseRedirect


class AjaxFormViewMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return self.render_to_json_response(
            {'success': False, 'form_html': form_html},
        )

    def form_valid(self, form):
        if hasattr(form, 'save'):
            self.object = form.save()
        return self.render_to_json_response(
            {'success': True, 'redirect_to': self.get_success_url()},
        )


@sensitive_post_parameters()
@csrf_protect
@never_cache
@json_view
def ajax_login(request, redirect_field_name=REDIRECT_FIELD_NAME,
        form_class=UserAuthenticationForm, template_name='accounts/login.html'):
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = form_class(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return {'success': True, 'redirect_to': redirect_to}
        else:
            form_html = render_crispy_form(form)
            return {'success': False, 'form_html': form_html}
    elif request.method == 'GET':
        return render_to_response(template_name, {'form': form_class(request)},
            context_instance=RequestContext(request))


@csrf_protect
@json_view
def ajax_registration(request, form_class=UserRegistrationForm,
                    redirect_to='/accounts/registration/complete/'):
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return {'success': True, 'redirect_to': redirect_to}
        else:
            form_html = render_crispy_form(form)
            return {'success': False, 'form_html': form_html}


def registration_complete(request, template_name='accounts/registration_complete.html',
                        **kwargs):
    return render_to_response(template_name,
                              kwargs,
                              context_instance=RequestContext(request))


def activate_complete(request, template_name='accounts/activate_complete.html', **kwargs):
    return render_to_response(template_name,
                              kwargs,
                              context_instance=RequestContext(request))


def activate(request, template_name='accounts/activate.html',
             success_url='/accounts/activate/complete/', extra_context=None, **kwargs):
    user = get_user_model().objects.activate_user(**kwargs)

    if user:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        if success_url is None:
            return redirect('/')
        else:
            return redirect(success_url)
    else:
        raise Http404

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              kwargs,
                              context_instance=context)


class ChangePasswordView(AjaxFormViewMixin, FormView):
    template_name = 'accounts/change_password.html'
    form_class = UserChangePasswordForm
    success_url = '/accounts/profile/'

    def form_valid(self, form):
        form.user_cache.set_password(form.cleaned_data['new_password2'])
        form.user_cache.save()
        return super(ChangePasswordView, self).form_valid(form)

    def get_initial(self):
        initial = super(ChangePasswordView, self).get_initial()
        initial['email'] = self.request.user.email
        return initial


@csrf_protect
@json_view
def password_reset(request, is_admin_site=False,
                   template_name='accounts/password_reset_form.html',
                   password_reset_form=GenericPassowrdResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect='/accounts/password/reset/done/',
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return {'success': True, 'redirect_to': post_reset_redirect}
        else:
            form_html = render_crispy_form(form)
            return {'success': False, 'form_html': form_html}
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='accounts/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=GenericSetPasswordForm,
                           post_reset_redirect='/accounts/password/done/',
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb36 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = UserModel._default_manager.get(pk=uid_int)
    except (ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def password_done(request, template_name='accounts/password_done.html',
        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def password_reset_done(request,
                        template_name='accounts/password_reset_done.html',
                        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
