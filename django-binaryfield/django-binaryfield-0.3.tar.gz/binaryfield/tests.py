"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from binaryfield import BinaryField
from binaryfield.hacks import memoryview

from django.conf import settings
from django.test import TestCase
from django.db import models
from django.core.validators import ValidationError

# a boolean for not managing Oracle tables
dont_manage = settings.DATABASES['default']['ENGINE'].endswith('oracle')

class DataModel(models.Model):

    short_data = BinaryField(max_length=10, default=b'\x08')
    data = BinaryField()

    class Meta:
        db_table = "test_data_model_blob"
        managed = not dont_manage


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        data_set = (self.binary_data, memoryview(self.binary_data))
        for bdata in data_set:
            dm = DataModel(data=bdata)
            dm.save()
            dm = DataModel.objects.get(pk=dm.pk)
            self.assertEqual(bytes(dm.data), bytes(bdata))
            # Resave (=update)
            dm.save()
            dm = DataModel.objects.get(pk=dm.pk)
            self.assertEqual(bytes(dm.data), bytes(bdata))
            # Test default value
            self.assertEqual(bytes(dm.short_data), b'\x08')

    def test_max_length(self):
        dm = DataModel(short_data=self.binary_data*4)
        self.assertRaises(ValidationError, dm.full_clean)

    def test_asign(self):
        dm = DataModel()
        dm.data = self.binary_data
        dm.short_data = self.binary_data
        dm.save()

        dmr = DataModel.objects.get(pk=dm.pk)
        self.assertEqual(bytes(dmr.data), bytes(dm.data))
