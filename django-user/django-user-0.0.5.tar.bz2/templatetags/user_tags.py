from django import template
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

register = template.Library()

@register.inclusion_tag('user/partial/sign_in.html')
def sign_in_form():
    return {'form': AuthenticationForm()}
    
@register.inclusion_tag('user/partial/sign_up.html')
def sign_up_form():
    return {'form': UserCreationForm()}
    
