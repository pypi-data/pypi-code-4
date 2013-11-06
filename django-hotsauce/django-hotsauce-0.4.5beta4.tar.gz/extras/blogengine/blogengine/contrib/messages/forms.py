from django import forms

class MessageForm(forms.Form):
    #username = forms.CharField(required=True)
    content = forms.CharField(required=True, max_length=300)

    #def clean_content(self, data):
    #    cleanded_data = super(MessageForm, self).clean_content(data)
    #    print "debug: cleaned_content: %r" % cleaned_data

