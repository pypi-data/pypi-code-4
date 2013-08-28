from datetime import datetime
from random import choice, sample
import string

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from nano.tools import pop_error, render_page, get_profile_model, asciify
from nano.user.forms import *
from nano.user import new_user_created

Profile = get_profile_model(raise_on_error=False)

class NanoUserError(Exception):
    pass

class NanoUserExistsError(NanoUserError):
    pass

# def pop_error(request):
#     error = request.session.get('error', None)
#     if 'error' in request.session:
#         del request.session['error']
#     return error

def random_password():
    sample_space = string.letters + string.digits + r'!#$%&()*+,-.:;=?_'
    outlist = []
    for i in xrange(1,8):
        chars = sample(sample_space, 2)
        outlist.extend(chars)
    return ''.join(outlist)

def make_user(username, password, email=None, request=None):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # make user
        user = User(username=username[:30])
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        if email:
            user.email = email
        user.save()
        if Profile:
            profile = Profile(user=user, display_name=username)
            profile.save()
        test_users = getattr(settings, 'NANO_USER_TEST_USERS', ())
        for test_user in test_users:
            if user.username.startswith(test_user):
                break
        else:
            new_user_created.send(sender=User, user=user) 
        if request is not None:
            messages.info(request, u"You're now registered, as '%s'" % username)
        return user
    else:
        raise NanoUserExistsError, "The username '%s' is already in use by somebody else" % username

def signup(request, template_name='signup.html', *args, **kwargs):
    me = 'people'
    error = pop_error(request)
    data = {
            'me': me, 
            'error': error, 
            'form': SignupForm()
    }
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            username = asciify(form.cleaned_data['username'])
            password = form.cleaned_data['password2']
            email = form.cleaned_data['email'].strip() or ''

            # check that username not taken
            userslug = slugify(username)
            if Profile.objects.filter(slug=userslug).count():
                # error!
                safe_username = slugify('%s-%s' % (username, str(datetime.now())))
                request.session['error'] = u"Username '%s' already taken, changed it to '%s'." % (username, safe_username)
                username = safe_username

            # make user
            user = make_user(username, password, email=email, request=request)
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            request.session['error'] = None
            next = getattr(settings, 'NANO_USER_SIGNUP_NEXT', reverse('nano_user_signup_done'))
            try:
                next_profile = user.get_profile().get_absolute_url()
                return HttpResponseRedirect(next_profile)
            except Profile.DoesNotExist:
                pass
            return HttpResponseRedirect(next)
    return render_page(request, template_name, data)

@login_required
def password_change(request, *args, **kwargs):
    error = pop_error(request)
    template_name = 'password_change_form.html'
    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data[u'password2']
            user = request.user
            user.set_password(password)
            user.save()
            request.session['error'] = None
            return HttpResponseRedirect('/password/change/done/')
    else:
        form = PasswordChangeForm()
    data = { 'form': form,
            'error': error,}
    return render_page(request, template_name, data)

def password_reset(request, project_name='Nano', *args, **kwargs):
    error = pop_error(request)
    template = 'password_reset_form.html'
    e_template = 'password_reset.txt'
    help_message = None
    e_subject = '%s password assistance' % project_name
    e_message = """Your new password is: 

%%s

It is long deliberately, so change it to 
something you'll be able to remember.


%s' little password-bot
""" % project_name
    e_from = getattr(settings, 'NANO_USER_EMAIL_SENDER', '')
    form = PasswordResetForm()
    if e_from and request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=form.cleaned_data['username'])
            if user.email:
                tmp_pwd = random_password()
                user.set_password(tmp_pwd)
                result = send_mail(subject=e_subject, from_email=e_from, message=e_message % tmp_pwd, recipient_list=(user.email,))
                user.save()
                request.session['error'] = None
                return HttpResponseRedirect('/password/reset/sent/')
            else:
                error = """There's no email-address registered for '%s', 
                        the password can't be reset.""" % user.username
                request.session['error'] = error
                
    data = {'form': form,
            'help_message': help_message,
            'error':error}
    return render_page(request, template, data)

