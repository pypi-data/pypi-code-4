
from django.conf.urls.defaults import *

from nano.faq.models import *

qa_dict = {
        'queryset': QA.objects.all().order_by('question'),
        'extra_context': {
                'me': 'faq',
                },
}

urlpatterns = patterns('django.views.generic',
        (r'^$',                     'list_detail.object_list', qa_dict),
)
