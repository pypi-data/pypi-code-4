from django.db import models

from conf import DRIVE_UPLOAD_URL, DRIVE_STATIC_URL
import form_fields

class S4DriveFileField(models.Field):
    def get_internal_type(self):
        return "TextField"

    def __init__(self, url=DRIVE_UPLOAD_URL, drive_static_url=DRIVE_STATIC_URL, *args, **kwargs):
        self.url = url
        self.drive_static_url = drive_static_url
        return super(S4DriveFileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.S4DriveFileField,
            "url": self.url,
            "drive_static_url": self.drive_static_url,
        }
        defaults.update(kwargs)
        return super(S4DriveFileField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.TextField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
