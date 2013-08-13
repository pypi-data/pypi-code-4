from django import forms
from django.utils.translation import ugettext_lazy as _

class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    It could be used also for derived MailUser models, it gets User model from
    settings.AUTH_USER_MODEL .
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.EmailField(label=_("Email"), max_length=254,
        help_text=_("Required. Valid email for registration and login."),
        error_messages={
            'invalid': _("This value must be a valid email address.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = django.contrib.auth.get_user_model()
        fields = ("email",)

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            settings.AUTH_USER_MODEL._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(MailUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    Changes user email and password
    """
    email = forms.EmailField(
        label=_("Email"), max_length=254,
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = django.contrib.auth.get_user_model()

    def __init__(self, *args, **kwargs):
        super(MailUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('profile_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AuthenticationForm(auth.contrib.forms.AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    
    Derives auth.contrib.AuthenticationForm and it is usable for
    username password sematic
    """
    pass


class PasswordResetForm(auth.contrib.forms.PasswordResetForm):
    """
    Derives auth.contrib.PasswordResetForm and it is usable for
    mail password sematic
    """
    pass


class SetPasswordForm(auth.contrib.forms.SetPasswordForm):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    pass

class PasswordChangeForm(django.contrib.auth.forms.PasswordChangeForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    pass


class AdminPasswordChangeForm(django.contrib.auth.forms.AdminPasswordChangeForm):
    """
    A form used to change the password of a user in the admin interface.
    """
    pass
