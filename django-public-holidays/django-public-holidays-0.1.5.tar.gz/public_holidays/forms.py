from django import forms
from models import PublicHoliday

import datetime

class PublicHolidayAdminForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(PublicHolidayAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['provinces'].widget = self.instance.country.provinces_filtered_select_multiple
            self.fields['provinces'].label = self.instance.country.provinces_name
            if self.instance.country.provinces_name:
                self.fields['provinces'].help_text.replace('province', self.instance.country.provinces_name)
        else:
            pass
            # We really want to load the list of states up when the country
            # has been chosen. But that can wait for another day.
    
