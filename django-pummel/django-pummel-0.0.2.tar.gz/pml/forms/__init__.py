from django.forms import Form
from django.template.loader import render_to_string
from pml.forms.fields import PMLCheckBoxField, PMLRadioField, PMLSelectField, PMLTextField


class PMLForm(Form):
    """
    Base PML which generates valid PML on a template {{ form }} call.

    @member header_text string: Text to display on form header.
    @member submit_text string: Text to display on submit button.
    """

    def __init__(self, *args, **kwargs):
        super(PMLForm, self).__init__(*args, **kwargs)

        # Attach errors to widgets
        for key, error in self.errors.items():
            self.fields[key].widget.error = error

    def __unicode__(self):
        """
        Renders valid PML form in its entirety.
        @returns string: safe PML.
        """
        return render_to_string("pml/form.xml", {'form': self})
