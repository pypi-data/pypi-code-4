from dendrite.backends import DendriteBackend
from .models import TwitterProfile, TestProfile

class TwitterBackend(DendriteBackend):
    profile_class = TwitterProfile
    
class TestBackend(DendriteBackend):
    profile_class = TestProfile
