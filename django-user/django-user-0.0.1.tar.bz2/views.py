from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
        
class SignUpView(FormView):
    form_class = UserCreationForm
    template_name = "user/sign_up.html"
    success_url = '/'
    
    def form_valid(self, form):
        form.save()
        
        response = super(SignUpView, self).form_valid(form)
        
        user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
                            
        auth_login(self.request, user)
        
        return response