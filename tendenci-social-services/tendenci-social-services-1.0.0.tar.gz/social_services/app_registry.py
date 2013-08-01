from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse

from .models import ReliefAssessment


class ReliefAssessmentRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Emergency Social Services Add-ON'

    url = {
        'add': lazy_reverse('social-services.form'),
        'search': lazy_reverse('social-services.map'),
    }

site.register(ReliefAssessment, ReliefAssessmentRegistry)
