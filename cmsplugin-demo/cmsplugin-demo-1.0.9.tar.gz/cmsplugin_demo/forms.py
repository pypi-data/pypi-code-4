from django import forms
from django.utils.translation import ugettext_lazy as _
#import settings
from cmsplugin_demo.nospam.forms import HoneyPotForm, RecaptchaForm, AkismetForm

CHOICES=[('Morning', 'Morning'),
         ('Evening', 'Evening'),
         ('No preference', 'No preference')]

  
class DemoForm(forms.Form):
    first_possibility = forms.DateField(label=_("First"), widget=forms.TextInput(attrs={'placeholder': 'first_possibility*(YYYY-MM-DD)','class':'form-control'}))
    first = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': 'unstyled'}))
    second_possibility = forms.DateField(label=_("Second"), widget=forms.TextInput(attrs={'placeholder': 'Second possiblity(YYYY-MM-DD)', 'class':'form-control'}), required=False)
    second = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': 'unstyled'}), required=False)
    name = forms.CharField(label=_("Name"), widget=forms.TextInput(attrs={'placeholder': 'Your name*', 'class':'form-control'}))
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'placeholder': 'Your email address*', 'class':'form-control'}))
    phone = forms.CharField(label=_("Phone"), widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class':'form-control'})) 
    remarks = forms.CharField(label=_("Remarks"), widget=forms.Textarea(attrs={'placeholder': 'Remarks*', 'class':'form-control'}))

    template = "cmsplugin_demo/contact.html"
  
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
