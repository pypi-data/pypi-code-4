import os
import re
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ReplacingViewPageTemplateFile(ViewPageTemplateFile):
    """ A page template that applies a regexp-based replacement when the
        template is loaded or modified.
    """

    regexp = None
    replacement = None

    def __init__(self, filename, _prefix=None, content_type=None,
                 module=None, regexp=None, replacement=None):

        if module is not None:
            _prefix = os.path.dirname(module.__file__)
        self.regexp = re.compile(regexp)
        self.replacement = replacement
        super(ViewPageTemplateFile, self).__init__(filename, _prefix)

    def write(self, text):
        text = self.regexp.sub(self.replacement, text)
        super(ViewPageTemplateFile, self).write(text)
