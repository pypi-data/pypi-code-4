try:
    import pinax.apps.account.forms
except:
    pass
else:
    from django import forms
    from django.utils.translation import ugettext_lazy as _, ugettext

    def snopp(self, *args, **kwargs):
            super(pinax.apps.account.forms.LoginForm, self).__init__(*args, **kwargs)
            ordering = []
            if pinax.apps.account.forms.EMAIL_AUTHENTICATION:
                self.fields["email"] = forms.EmailField(
                    label = ugettext("E-mail"),
                )
                ordering.append("email")
            else:
                self.fields["username"] = forms.CharField(
                    label = ugettext("Username"),
                    max_length = 320,
                )
                ordering.append("username")
            ordering.extend(["password", "remember"])
            self.fields.keyOrder = ordering

    pinax.apps.account.forms.LoginForm.__init__ = snopp


