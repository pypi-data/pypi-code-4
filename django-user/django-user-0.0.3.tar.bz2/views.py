from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.forms import HiddenInput

from user.forms import ProfileForm

class SignInView(FormView):
    form_class = AuthenticationForm
    success_url = '/'
    
    def get_form(self, *args):
        form = super(SignInView, self).get_form(self.get_form_class())
        fields = form.fields
        fields['username'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Username'
        }
        
        fields['password'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Password'
        }
        
        return form
        
    def form_valid(self, form):
        response = super(SignInView, self).form_valid(form)
        
        auth_login(self.request, form.get_user())
        
        messages.add_message(self.request, messages.SUCCESS, 'Sign In was successful!')
        
        return HttpResponseRedirect(self.request.POST.get('next') or self.request.GET.get('next') or reverse('profile'))
        
        
class SignUpView(FormView):
    form_class = UserCreationForm
    success_url = '/'
    
    def get_form(self, *args):
        form = super(SignUpView, self).get_form(self.get_form_class())
        fields = form.fields
        fields['username'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Username'
        }
        
        fields['password1'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Password'
        }
        
        fields['password2'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }
        
        return form
        
    def form_valid(self, form):
        form.save()
        
        self.success_url = reverse('profile')
        
        response = super(SignUpView, self).form_valid(form)
        
        user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
                            
        auth_login(self.request, user)
        
        messages.add_message(self.request, messages.SUCCESS, 'Sign Up was successful!')
        
        return response
 
 
class ProfileView(FormView):
    form_class = ProfileForm
    success_url = '/'
    
    def get_form(self, *args):
        self.success_url = reverse('profile')
        form = super(ProfileView, self).get_form(self.get_form_class())
        fields = form.fields
        user = self.request.user
        
        placeholders = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address'
        }
        
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username
        }
        
        form.initial = initial
        
        for field in fields.keys():
            if field in placeholders.keys():
                fields[field].widget.attrs = {
                    'class': 'form-control',
                    'placeholder': placeholders[field]
                }
            else:
                del fields[field]
        
        return form
    
    
    def form_invalid(self, form):
        print 'invalid'
        print form._errors
        response = super(ProfileView, self).form_invalid(form)
        return response
        
    
    def form_valid(self, form):
        response = super(ProfileView, self).form_valid(form)
        
        form.save(self.request.user)
        
        messages.add_message(self.request, messages.SUCCESS, 'Profile Change was successful!')
        
        return response
        