from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe
from django.conf import settings


class S4DriveFileWidget(Widget):
    def __init__(self, url, drive_static_url, **kwargs):
        self.url = url
        self.drive_static_url = drive_static_url
        return super(S4DriveFileWidget, self).__init__(**kwargs)

    def render(self, name, value, attrs=None):
        if not value: value = ""
        return mark_safe(loader.render_to_string("django_s4/s4_drive_file.html", {
            "STATIC_URL": settings.STATIC_URL,
            "DRIVE_STATIC_URL": self.drive_static_url,
            "name": name,
            "url": self.url,
            "value": value,
        }))