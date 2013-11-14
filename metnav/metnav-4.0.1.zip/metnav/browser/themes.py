# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from Globals import DevelopmentMode
from logging import getLogger

from Products.Five import BrowserView
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.interface import Interface
from metnav.functions import myGetSearchableText

logger = getLogger('Themes browser')

class IThemeBrowserView(Interface):
    """ marker interface """


class Themes(BrowserView):

    implements(IThemeBrowserView)

    def themes(self, parts='', object_type='', media='', termes='', sort_order='$date descending', nb_limit=0, start=0, output='page'):
        context = self.context
        mn_tool = getToolByName(context, 'portal_metadataNav')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        base = mn_tool.getDA()
        BASE = "xmldb:exist://%s" % base.server
        self.site_url = self.portal_state.portal_url()
        #self.collection=mn_tool.getCollection(REQUEST)
        
        if parts in ('','//') and object_type == '' and media=='':
            return ''

        taxons = parts.strip().split('//')
        if len(taxons)>2:
            taxons=taxons[2:]
        else:
            taxons=taxons[1:]          
        taxons.reverse()
        if taxons == [] and object_type.strip() == '':
            return ""

        parts_xq = ""
        for taxon in taxons:
            if taxon.strip() != '':
                #parts_xq += """[contains(lom:taxon/lom:entry/lom:string/text(), "%s")]""" % taxon
                parts_xq += """[lom:taxon/lom:entry/lom:string/text()="%s"]""" % taxon
                
        termesQuery=""
        termes=termes.strip()
        if termes !='':
            #Pour Générer les résultats plus rafinés ou plus pertinents
            if termes.find('AND')==-1 and termes.find('+')==-1 and termes.find('OR')==-1:
                termes=termes.replace(' ', '+')
                
            termesQuery+="""[ft:query(., "%s") or fn:matches(., "%s")]""" % (termes, myGetSearchableText(termes))
            
        if object_type == '':
            objects = ''
            if media=='':
                objects = ''
            elif media=='texte':
                objects = """[(.//lomfrens:value="article") or (.//lomfrens:value="%s")]""" % media
            else: 
                objects ="""[.//lomfrens:value="%s"]""" % media
        else:
            if media=='':
                objects = """[.//lomfrens:value="%s"]""" % object_type
                #if object_type=='diaporama':
                #    objects = """[contains(lomfrens:ensData/lomfrens:ensDocumentType, "diaporama") or #contains(lomfrens:ensData/lomfrens:ensDocumentType, "albumImage")]"""
            else:
                objects = """[(.//lomfrens:value="%s") and (.//lomfrens:value="%s")]""" % (object_type, media)
                #if object_type=='diaporama':
                #    objects = """[contains(lomfrens:ensData/lomfrens:ensDocumentType, "diaporama") or #contains(lomfrens:ensData/lomfrens:ensDocumentType, "albumImage") and contains(lomfrens:ensData/lomfrens:ensDocumentType, #"%s")]""" % (media)
                #else: 
                #    objects = """[contains(lomfrens:ensData/lomfrens:ensDocumentType, "%s") and #contains(lomfrens:ensData/lomfrens:ensDocumentType, "%s")]""" % (object_type, media)
       

        # context.template.__str__() is waiting for unicode or ascii data
        # Query returns UTF-8 strings then you must decode them
        params_dict = {
            'XSL':output,
            'XSL_PARAMS': {
                'rss.title': u"Ressources par thème",
                'rss.desc': u'Ressources du site classées par thèmes',
                'rss.copyright': u'Mon établissement',
                },
            'NB_LIMIT':nb_limit,
            'START':start,
            'PARTS': parts_xq.decode('utf-8'),
            'TERMES':termesQuery,
            'OBJECTS': objects.decode('utf-8'),
            'BASE':BASE,
            'TRI':sort_order,
            'site_url':self.site_url,
        }

        query = context.xq_classification.__str__() % mn_tool.getQueryParams(params_dict, context.REQUEST)
        
        if DevelopmentMode:
            logger.info('\nREQUEST\n' + query)

        da = mn_tool.getDA()

                # ExistDA is waiting for UTF-8
        res = da.query(query.encode('utf-8'), object_only=1)
        liste_dico=res.getDict()
        retour = []
        for dico in liste_dico:
            retour.append(dico)
            
        if len(retour) == 0 and len(liste_dico) > 0:
                return liste_dico

        if DevelopmentMode:
            if str(res):
                logger.info('\nRESULTS\n' + str(res))
            else:
                logger.info('\nNO RESULT\n')
        #return str(res)
        return retour