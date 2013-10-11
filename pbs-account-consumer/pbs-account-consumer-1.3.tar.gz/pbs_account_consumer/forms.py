from django import forms


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    new_password_again = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        new_password_again = cleaned_data.get("new_password_again")
        if new_password != new_password_again:
            raise forms.ValidationError("New passwords do not match")
        return cleaned_data
