""" FaqEntry ContentType  """

from interfaces import IFaqEntry
from zope.interface import implements
from Products.ATContentTypes.atct import ATCTContent, ATContentTypeSchema
from Products.Archetypes.public import Schema, \
                                       RichWidget, registerType, TextField

from Products.Faq import config
from Products.Faq import faqMessageFactory as _

schema = ATContentTypeSchema.copy() + Schema((

    TextField('answer',
              primary=1,
              required=1,
              searchable=1,
              default_content_type="text/html",
              default_output_type='text/x-html-safe',
              allowable_content_types=("text/plain", "text/html"),
              widget=RichWidget(
                      label=_(_(u'label_answer'), default=u'Answer'),
                      description=_(u"desc_answer", 
                                   default=u"Meaningful sentences that " + \
                                           u"explains the answer."),
                      width='100%',
                      rows=10),
              ),
    ))


schema['title'].widget.label = _(u'label_question', default=u'Question')
schema['title'].widget.description = _(u'desc_question', 
                                       default=u'The frequently asked question.')

schema['description'].widget.label = _(u'label_detailed_question',
                                       default=u'Detailed Question')
schema['description'].widget.description = _(u'desc_detailed_question',
                                     default=u'More details on the question, '
                                             u'if not evident from the title.')

class FaqEntry(ATCTContent):

    implements(IFaqEntry)
    schema = schema

registerType(FaqEntry, config.PROJECTNAME)
