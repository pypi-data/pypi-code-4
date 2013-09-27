from django.contrib.auth.backends import ModelBackend

class DendriteBackend(ModelBackend):
    """
    Default backend that allows authenticating with social profiles.
    Only expectation is that the backend receives a profile class and
    an ID to check against. 
    """
    profile_class = None

    def __init__(self):
        assert self.profile_class, "Please specify a `profile_class` attribute with "\
            "this authentication backend"

    def authenticate(self, id=None, profile_class=None, **kwargs):
        if not profile_class == self.profile_class:
            return

        try:
            return self.profile_class.objects.get(id=id).user
        except self.profile_class.DoesNotExist:
            return None

