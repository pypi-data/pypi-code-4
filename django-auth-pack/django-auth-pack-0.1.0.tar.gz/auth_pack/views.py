from jsonview.decorators import json_view
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
from auth_pack.forms import UserRegistrationForm, UserAuthenticationForm


@sensitive_post_parameters()
@csrf_protect
@never_cache
@json_view
def ajax_login(request, redirect_field_name=REDIRECT_FIELD_NAME, form_class=UserAuthenticationForm):
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


@csrf_protect
@json_view
def ajax_registration(request, form_class=UserRegistrationForm):
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return {'success': True, 'redirect_to': '/'}
        else:
            form_html = render_crispy_form(form)
            return {'success': False, 'form_html': form_html}


def activate(request, template_name='accounts/activate.html',
             success_url=None, extra_context=None, **kwargs):
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
