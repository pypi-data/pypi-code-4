# -*- coding: utf-8 -*-
# $Id: interfaces.py 116942 2010-05-05 15:30:13Z glenfant $
"""Public interfaces for PDFBook"""

from zope.interface import Interface
from zope.schema import Tuple
from zope.schema import Bool
from zope.schema import ASCIILine
from zope.schema import Text
from zope.schema import Choice

from aws.pdfbook import translate as _

class IPDFOptions(Interface):
    """Misg global options for PDF rendering
    """

    disallowed_types = Tuple(
        title=_(u'label_disallowed_types', default=u"Discarded content types"),
        description=_(u'help_disallowed_types', default=u"Select content types that will not be rendered"),
        value_type=Choice(vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes")
        )

    recode_path = ASCIILine(
        title=_(u'label_recode_path', default=u"\"recode\" executable"),
        description=_(
            u'help_recode_path',
            default=(
                u"The full absolute path to the \"recode\". executable"
                u"On Unix \"which recode\" should provide the good value."
                )
            ),
        default="/usr/bin/recode"
        )

    htmldoc_path = ASCIILine(
        title=_(u'label_htmldoc_path', default=u"\"htmldoc\" executable"),
        description=_(
            u'help_htmldoc_path',
            default=(
                u"The full absolute path to the \"htmldoc\" executable. "
                u"On Unix \"which htmldoc\" should provide the good value"
                )
            ),
        default="/usr/bin/htmldoc"
        )

    htmldoc_options = Text(
        title=_(u'htmldoc_options', default=u"Options for htmldoc"),
        description=_(
            u'help_htmldoc_options',
            default=(
                u"See the htmldoc documentation <http://www.htmldoc.org/documentation.php/toc.html>."
                u" but do not add the \"-f\" option here."
                )
            ),
        required=False
        )

class IAWSPDFBookLayer(Interface):
    """Layer for views used in PDFBook"""
    pass

class IPDFTransformer(Interface):
    """Class that transforms content to PDF
    """
    pass


class IPrintOptions(Interface):
    """Misc options for printing
    """

    inline_render = Bool(
        title=_(u'label_inline_render', default=u"Render PDF in the browser"),
        description=_(
            u'help_inline_render',
            default=(
                u"This works only if you installed Adobe Acrobat as browser plugin."
                u" If this does not work, (i.e you got the download dialog), this is not a bug."
                )
            ),
        default=False
        )
    pass
