from django.forms.fields import Field
from djinn_forms.widgets.image import ImageWidget


class ImageField(Field):

    """ Convert given value to image """

    widget = ImageWidget

    def __init__(self, model=None, **kwargs):

        super(ImageField, self).__init__(**kwargs)

        self.model = model

    def prepare_value(self, data):

        if hasattr(data, "file"):
            return data
        else:
            return ""

    def to_python(self, value):

        try:
            return self.model.objects.get(pk=value).image        
        except:
            return None
