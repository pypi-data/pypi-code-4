from lxml import etree

from django import forms
from django.db import models


class XMLFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema')
        super(XMLFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(XMLFileField, self).clean(*args, **kwargs)

        with data as fh:
            doc = etree.parse(fh)

        with open(self.schema) as fh:
            schema = etree.XMLSchema(etree.parse(fh))

        if not schema.validate(doc):
            raise forms.ValidationError('The XML file failed to validate '
                                        'against the supplied schema.')
        return data
