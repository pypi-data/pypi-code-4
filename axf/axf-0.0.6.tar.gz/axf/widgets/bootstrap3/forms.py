import tw2.core as twc
from tw2.forms.widgets import BaseLayout, Form


class HorizontalLayout(BaseLayout):
    __doc__ = """
    Arrange widgets and labels in bootstrap3 horizontal- layout.
    """ + BaseLayout.__doc__

    template = "axf.widgets.bootstrap3.templates.horizontal_layout"


class HorizontalForm(Form):
    """Equivalent to a Form containing a HorizontalLayout."""
    child = twc.Variable(default=HorizontalLayout)
    children = twc.Required

    labels_css_class = twc.Param(
        'label css class',
        default='col-lg-2'
    )

    input_wrappers_class = twc.Param(
        'input wrapper css class',
        default='col-lg-10'
    )

    display_errors = twc.Param(
        'display error messages in help block',
        default=True
    )

    css_class = 'form-horizontal'
