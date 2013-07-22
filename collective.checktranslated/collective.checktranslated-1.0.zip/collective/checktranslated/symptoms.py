# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from collective.jekyll.symptoms import SymptomBase

from collective.checktranslated import checktranslatedMessageFactory as _

STATUS = {'correct': True, 'warning': 'warning', 'error': False}


class HasTranslated(SymptomBase):
    title = _(u"Translation")
    help = _(u"This object should be translated into all site languages.")

    def _update(self):
        site = getSite()
        languages = site.portal_languages.getAvailableLanguages().keys()
        self.status, self.description = check_translated(self.context,
                                                              languages)


def check_translated(context, languages):
    site_languages = languages
    obj_lang = context.Language()
    status = ''
    description = []

    if len(site_languages) == 1 and obj_lang != '':
        status = STATUS['error']
        #status = STATUS['warning']
        msgid = _(u"There is only one language installed on your site.")
        desc = context.translate(msgid)
        return status, desc
    if obj_lang == '':
        status = STATUS['error']
        msgid = _(u"This is a neutral language object.")
        desc = context.translate(msgid)
        return status, desc

    if obj_lang not in site_languages:
        status = STATUS['error']
        msgid = _(u"Language not installed.")
        desc = context.translate(msgid)
        return status, desc

    for lang in languages:
        if hasattr(context, 'getTranslation'):
            translate_context = context.getTranslation(lang)
            if translate_context is None:
                status = STATUS['error']
                msgid = _(u"There is no {0} translation".format(lang))
                description.append(context.translate(msgid))
    if len(description) == 0:
        status = STATUS['correct']
        msgid = _(u"Translated into all languages.")
        description.append(context.translate(msgid))
    return status, ", ".join(description)
