# AuthoringPublishedContent is implictly addable since
# folder contraints don't work as it should. Therefore
# we filter out the menu entry here....evil hack but
# working

from plone.app.content.browser import folderfactories
from plone.memoize.request import memoize_diy_request
blacklisted_types = ['AuthoringPublishedDocument']

@memoize_diy_request(arg=0)
def _allowedTypes(request, context):
    results = context.allowedContentTypes()
    results = [r for r in results if r.content_meta_type not in blacklisted_types]
    return results

folderfactories._allowedTypes = _allowedTypes

