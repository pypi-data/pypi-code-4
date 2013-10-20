# -*- coding: utf-8 -*-
"""
reStructuredText parser facilities

Requires :

* docutils from http://docutils.sf.net/
"""
import copy

try:
    from xml.etree.cElementTree import fromstring, tostring, ElementTree
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring, ElementTree

from django.utils.encoding import smart_str

import docutils
import docutils.core
import docutils.nodes
import docutils.utils
import docutils.parsers.rst

import Sveetchies.django.documents.utils.rest_roles

from Sveetchies.django.documents import DOCUMENTS_PARSER_FILTER_SETTINGS

# Si Pygments n'est pas installé, pas d'exception levée et sa directive n'est donc pas 
# activée
try:
    import Sveetchies.django.documents.utils.pygments_directive
except ImportError:
    pass

def get_functional_settings(setting_key, body_only, initial_header_level, silent):
    """
    Méthode de traitement d'une source de texte par le parser
    
    Renvoi l'instance retournée par le parser, avec son contenu et suppléments
    """
    parser_settings = copy.deepcopy(DOCUMENTS_PARSER_FILTER_SETTINGS[setting_key])
    parser_settings.update({'halt_level':6, 'enable_exit':0})
    if silent:
        parser_settings.update({'report_level': 5})
    if initial_header_level:
        parser_settings['initial_header_level'] = initial_header_level
    return parser_settings

def SourceParser(source, setting_key="default", body_only=True, initial_header_level=None, silent=True):
    """
    Méthode de traitement d'une source de texte par le parser
    
    Renvoi l'instance retournée par le parser, avec son contenu et suppléments
    """
    parser_settings = get_functional_settings(setting_key, body_only, initial_header_level, silent)
    
    #toc = extract_toc(source, parser_settings)
    parts = docutils.core.publish_parts(source=smart_str(source), writer_name="html4css1", settings_overrides=parser_settings)

    if body_only:
        return parts['fragment']
    return parts

def extract_toc(source, setting_key="default", body_only=True, initial_header_level=None, silent=True):
    """
    Récupère le sommaire (TOC: Table Of Content) généré à partir des titres de sections
    
    Actuellement c'est très gruik :
    
    * Pas de possibilité évidente d'avoir le TOC en dehors du document via la 
      directive ``contents`` donc cette méthode parse de son coté la source en lui 
      ajoutant cette directive au tout début;
    * Le résultat est parsé comme du ElementTree pour y retrouver le bloc concernant le 
      TOC et l'extraire;
    * Comme la recherche Xpath n'est pas assez développé dans le ElementTree embarqué dans 
      Python 2.6, on assume que le premier bloc est toujours celui du TOC (à ma 
      connaissance ce n'est pas possible autrement);
    """
    parser_settings = get_functional_settings(setting_key, body_only, initial_header_level, silent)
    
    toc_internal_id = "private-page-toc-menu"
    source = u".. contents:: {tocid}\n\n{source}".format(tocid=toc_internal_id, source=source)
    parts = docutils.core.publish_parts(source=smart_str(source), writer_name="html4css1", settings_overrides=parser_settings)

    extracted = fromstring((u"<div id=\"document_root_body\">"+parts['fragment']+u"</div>").encode('utf-8')).find("div")
    if extracted and 'id' in extracted.keys() and extracted.get("id") == toc_internal_id:
        return tostring(extracted.find("ul"), encoding="UTF-8").replace("<?xml version='1.0' encoding='UTF-8'?>", '').strip()
    
    return ''

class SilentReporter(docutils.utils.Reporter):
    """
    Rapporteur d'erreurs silencieux mais qui mémorise chaque erreur pour pouvoir les 
    exploiter par la suite sans avoir à consulter le rendu du contenu.
    """
    def __init__(self, source, report_level, halt_level, stream=None,
                    debug=0, encoding='ascii', error_handler='replace'):
        self.messages = []
        docutils.utils.Reporter.__init__(self, source, report_level, halt_level, stream,
                            debug, encoding, error_handler)

    def system_message(self, level, message, *children, **kwargs):
        self.messages.append((level, message, children, kwargs))

def SourceReporter(data, setting_key="default"):
    """
    Détection d'éventuelles erreurs de syntaxe dans le contenu soumis
    
    Renvoi une liste d'erreurs si il y'en
    
    TODO: * Devrait renvoyer tout les avertissements et pas s'arrêter de parser dès la 
            première erreur;
          * Manque l'application des settings d'options possibles;
          * à mieux calibrer parce qu'en l'état je ne suis pas trop sûr du paramétrage 
            appliqué au parser et reporter;
    """
    source_path = None
    parser = docutils.parsers.rst.Parser()
    settings = docutils.frontend.OptionParser().get_default_values()
    settings.tab_width = 4
    settings.pep_references = None
    settings.rfc_references = None
    reporter = SilentReporter(
        source_path,
        settings.report_level,
        settings.halt_level,
        stream=settings.warning_stream,
        debug=settings.debug,
        encoding=settings.error_encoding,
        error_handler=settings.error_encoding_error_handler
    )

    document = docutils.nodes.document(settings, reporter, source=source_path)
    document.note_source(source_path, -1)
    try:
        parser.parse(data, document)
    except AttributeError:
        pass
    except TypeError:
        # Pour une raison inconnue le SilentReporter a un problème avec les roles 
        # locaux, donc on est obligé de capturer aussi les ``TypeError``
        pass
    return reporter.messages

def map_parsing_errors(error):
    """
    Remappe la liste des erreurs de syntaxe fournis par le parser pour qu'elles soient 
    plus "présentables"
    """
    code, message, content, source = error
    return u"Ligne {lineno} : {message}".format(lineno=source.get('line', 0), message=message)
