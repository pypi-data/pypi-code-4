
import re

from django.template import RequestContext

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode
from django.utils.translation import get_language, activate

from haystack import indexes, connections
from cms.models.pluginmodel import CMSPlugin
from cms.models.titlemodels import Title

try:
    from django.test.client import RequestFactory
except ImportError:
    from cmsplugin_search.utils import RequestFactory

def _strip_tags(value):
    """
    Returns the given HTML with all tags stripped.

    This is a copy of django.utils.html.strip_tags, except that it adds some
    whitespace in between replaced tags to make sure words are not erroneously
    concatenated.
    """
    return re.sub(r'<[^>]*?>', ' ', force_unicode(value))


rf = RequestFactory()

class PageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    excerpt = indexes.CharField(stored=True, indexed=False)
    pub_date = indexes.DateTimeField(model_attr='page__publication_date', null=True)
    login_required = indexes.BooleanField(model_attr='page__login_required')
    title = indexes.CharField(stored=True, indexed=False, model_attr='page__get_title')
    site_id = indexes.IntegerField(stored=True, indexed=True, model_attr='page__site_id')
    language = indexes.CharField(stored=True, indexed=True, model_attr='language')

    def prepare(self, obj):
        request = rf.get("/")
        request.session = {}
        self.prepared_data = super(PageIndex, self).prepare(obj)
        plugins = CMSPlugin.objects.filter(language=obj.language, placeholder__in=obj.page.placeholders.all())
        text = ''
        for plugin in plugins:
            instance, _ = plugin.get_plugin_instance()
            if hasattr(instance, 'search_fields'):
                text += u''.join(force_unicode(_strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
            if getattr(instance, 'search_fulltext', False):
                text += _strip_tags(instance.render_plugin(context=RequestContext(request)))
        text += "\n" + obj.title
        self.prepared_data['text'] = text
        # Prepare an extract/excerpt for use in results
        self.prepared_data['excerpt'] = text[:350].rsplit(" ", 1)[0] + " ..."
        return self.prepared_data

    def get_model(self):
        return Title

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(page__publisher_is_draft=False).distinct()



