# -*- coding: utf-8 -*-
#
#  This file is part of django-mysql-manager.
#
#  django-mysql-manager is a Django based management interface for MySQL users and databases.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-mysql-manager
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-mysql-manager
#
#  Copyright 2011 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import string

from django import forms
from django.db.models.loading import cache

from mysql_manager import settings


class MySQLUserModelForm(forms.ModelForm):

    class Meta:
        model = cache.get_model('mysql_manager', 'MySQLUser')
    
    # Adds two extra password fields, which will be used for password confirmation.
    password1 = forms.CharField(label='Password', required=False, widget=forms.PasswordInput, help_text="Valid characters a-z, A-Z, 0-9 and the underscore '_'")
    password2 = forms.CharField(label='Password (confirm)', required=False, widget=forms.PasswordInput, help_text="Valid characters a-z, A-Z, 0-9 and the underscore '_'")
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name.lower() in settings.MYMANAGER_FORBIDDEN_USER_NAMES:
            forms.ValidationError('This name is reserved for internal use.')
        return name
    
    def clean_password1(self):
        """Assures that passord characters are: a-z, A-Z, 0-9
        """
        password1 = self.cleaned_data.get('password1')
        if password1:
            valid_chars = string.lowercase + string.uppercase + string.digits + '_'
            for character in password1:
                if character not in valid_chars:
                    self._errors['password1'] = self.error_class(['Valid characters a-z, A-Z, 0-9.'])
        return password1
        
    def clean_password2(self):
        """Cleans the content of the two extra password fields.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        # Provided password and confirmation must match
        if password1 != password2:
            raise forms.ValidationError('The two password fields do not match.')
        
        # Password is required on new records!
        # If a password has not been set...
        if not password1 and not password2:
            if self.instance.pk is None: # ... and this is a new record
                # Attach error messages to the password fields
                self._errors['password1'] = self.error_class(['Password must be set on new records.'])
                self._errors['password2'] = self.error_class(['Password must be set on new records.'])
                
        return password2



class MySQLDatabaseModelForm(forms.ModelForm):

    class Meta:
        model = cache.get_model('mysql_manager', 'MySQLDatabase')
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name.lower() in settings.MYMANAGER_FORBIDDEN_DATABASE_NAMES:
            forms.ValidationError('This name is reserved for internal use.')
        return name


