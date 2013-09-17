from django.contrib.auth.forms import UserChangeForm

class ProfileForm(UserChangeForm):
    def save(self, *args):
        user_session = args[0]
        
        user_session.first_name = self.cleaned_data['first_name']
        user_session.last_name = self.cleaned_data['last_name']
        user_session.email = self.cleaned_data['email']
            
        user_session.save()