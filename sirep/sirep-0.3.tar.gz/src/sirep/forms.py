from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext_lazy as _

class ReportForm(forms.Form):
    """
    Report form. Our sirep.base.Report class is request responsive, thus we need this form purely
    to modify the GET parameters (and validate the filtered data of course).

    Each form shall get the report (sirep.base.Report) object as as argument (argument name "report") in
    order to find out wheither the date filtering shall be applied or not. This is simply checked by presence of the
    ``date_field`` attribute in the given ``Report`` object.
    """
    def __init__(self, *args, **kwargs):
        report = None
        if kwargs.has_key('report'):
            report = kwargs.pop('report')
        super(ReportForm, self).__init__(*args, **kwargs)
        if report and hasattr(report, 'date_field') and report.date_field not in ('', None):
            self.fields['date_lower'] = forms.DateField(label=_("From date (lower)"), required=False, \
                                                        widget=widgets.AdminDateWidget())
            self.fields['date_upper'] = forms.DateField(label=_("To date (upper)"), required=False, \
                                                        widget=widgets.AdminDateWidget())

        self.fields['per_page'] = forms.IntegerField(label=_("Limit (max number of results)"), required=False, \
                                                     widget=widgets.AdminTextInputWidget(attrs={'class': 'short'}))
        self.fields['page'] = forms.IntegerField(label=_("Page number"), required=False, \
                                                 widget=widgets.AdminTextInputWidget(attrs={'class': 'short'}))
