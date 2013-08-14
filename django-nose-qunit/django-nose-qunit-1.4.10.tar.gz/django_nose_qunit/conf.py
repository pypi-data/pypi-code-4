from django.conf import settings as django_settings


class LazySettings(object):

    @property
    def QUNIT_DYNAMIC_REGISTRY(self):
        return getattr(django_settings, "QUNIT_DYNAMIC_REGISTRY",
                       django_settings.DEBUG)

settings = LazySettings()
