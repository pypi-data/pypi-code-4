from django.contrib import admin
from archer.custom_auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django import forms
from guardian.admin import GuardedModelAdmin


class CustomUserChangeForm(UserChangeForm):
    username = forms.RegexField(
        label=_("Username"), max_length=200, regex=r"^[\w.@+-=/ ]+$",
        help_text=_("Required. 200 characters or fewer. Letters, digits and "
                    "@/./+/-/_/=/ // only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_/=/ // characters.")})


class CustomUserCreationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=200,
                                regex=r'^[\w.@+-=/ ]+$',
                                help_text=_("Required. 200 characters or fewer. Letters, digits and "
                                            "@/./+/-/_/=/ // only."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_/=/ // characters.")})

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    class Meta(UserCreationForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin, GuardedModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


admin.site.register(User, CustomUserAdmin)
