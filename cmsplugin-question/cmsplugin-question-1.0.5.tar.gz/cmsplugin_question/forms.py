from django import forms
from django.utils.translation import ugettext_lazy as _
#import settings
from cmsplugin_question.nospam.forms import HoneyPotForm, RecaptchaForm, AkismetForm
  
class ContactForm(forms.Form):
    name = forms.CharField(label=_("Name"), widget=forms.TextInput(attrs={'placeholder': 'Your name*', 'class':'form-control'}))
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'placeholder': 'Your email address*', 'class':'form-control'}))
    phone = forms.CharField(label=_("Phone"), widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class':'form-control'})) 
    question = forms.CharField(label=_("Question"), widget=forms.Textarea(attrs={'placeholder': 'Question', 'class':'form-control'}))

    template = "cmsplugin_question/contact.html"
  
class HoneyPotContactForm(HoneyPotForm):
    pass

class AkismetContactForm(AkismetForm):
    akismet_fields = {
        'comment_author_email': 'email',
        'comment_content': 'content'
    }
    akismet_api_key = None
    

class RecaptchaContactForm(RecaptchaForm):
    recaptcha_public_key = None
    recaptcha_private_key = None
    recaptcha_theme = None
