from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex

from case_studies.models import CaseStudy, Image

class CaseStudyIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    client = indexes.CharField(model_attr='client')

site.register(CaseStudy, CaseStudyIndex)
site.register(Image)
