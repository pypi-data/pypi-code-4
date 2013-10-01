# -*- coding: utf-8 -*-

import django.forms as forms
import models as mymodels
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

class SignupForm(forms.ModelForm):

    class Meta:
        model = mymodels.UserProfile
        fields = ('twitter', 'avatar', 'signature')

    def save(self, user):
        instance = user.get_profile()
        instance.twitter = self.cleaned_data['twitter']
        instance.avatar = self.cleaned_data['avatar']
        instance.signature = self.cleaned_data['signature']
        instance.save()
        return instance

class ProfileForm(forms.ModelForm):

    class Meta:
        model = mymodels.UserProfile
        fields = ('twitter', 'avatar', 'signature')
