from django import forms
from django.utils.translation import ugettext_lazy as _
#import settings
from cmsplugin_price.nospam.forms import HoneyPotForm, RecaptchaForm, AkismetForm

CHOICES=[('1', 'Morning'),
         ('2', 'Evening'),
         ('3', 'No preference')]

  
class PriceForm(forms.Form):
    name = forms.CharField(label=_("Name"), widget=forms.TextInput(attrs={'placeholder': 'Your name*', 'class':'form-control'}))
    phone = forms.CharField(label=_("Phone"), widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class':'form-control'}), required=False)
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'placeholder': 'Your email address*', 'class':'form-control'})) 
    number_of_students = forms.IntegerField(label=_("number of students"), widget=forms.TextInput(attrs={'placeholder': 'Number of Students', 'class':'form-control'})) 
    schoolname = forms.CharField(label=_("Schoolname"), widget=forms.TextInput(attrs={'placeholder': 'Schoolname*', 'class':'form-control'}))
    remarks = forms.CharField(label=_("Remarks"), widget=forms.Textarea(attrs={'placeholder': 'Remarks*', 'class':'form-control'}))
    template = "cmsplugin_price/contact.html"
  
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
