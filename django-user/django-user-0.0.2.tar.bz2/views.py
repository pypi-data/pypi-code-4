from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User

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
        
        return HttpResponseRedirect(self.request.POST.get('next') or self.request.GET.get('next') or self.success_url)
        
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
        
        response = super(SignUpView, self).form_valid(form)
        
        user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
                            
        auth_login(self.request, user)
        
        return response