# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.
from Globals import DevelopmentMode
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from metnav.browser.themes import IThemeBrowserView

class IRelatedPortlet(IPortletDataProvider):
    """
    A portlet displaying a the top news
    """

class Assignment(base.Assignment):
    implements(IRelatedPortlet)
    title = _(u'Related')

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/related.pt')

    def render(self):
        return self._template()

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()

    @property
    def metnav_properties(self):
        return getToolByName(self.context, 'portal_properties').metnav_properties

    def related(self,meta_url, start=1, nb_limit=0, output='portlet'):
        context = self.context
        mn_tool = getToolByName(context, 'portal_metadataNav')
        mn_props = getToolByName(context, 'portal_properties').metnav_properties
        collection = mn_props.getProperty('COLLECTION_METADATA')

        params_dict = {'XSL':output,
                            'XSL_PARAMS':{'rss.title':"Voir aussi",
                                          'rss.desc':u'Documents connexes',
                                          'rss.copyright':u'Mon établissement',},
                            'NB_LIMIT':nb_limit,
                            'START':start,
                            'SCORE_CONNEXE':mn_props.getProperty('SCORE_CONNEXE', 10),
                            'META_URL':meta_url,
                            'COLLATION':'',
                           }
                          

        #query = (str(context.xq_related) % mn_tool.getQueryParams(params_dict, self.request))
        query = context.xq_related.__str__() %  {
            'META_URL':meta_url,
            'SCORE_CONNEXE':mn_props.getProperty('SCORE_CONNEXE', 10),
            'COLLECTION':collection,
            'site_url': self.site_url,
            }


        da = mn_tool.getDA()
        results = da.query(query.encode('utf-8'))
        
        liste_dico=results.getDict()
        retour = []
        for dico in liste_dico:
            retour.append(dico)
            
        if len(retour) == 0 and len(liste_dico) > 0:
                return liste_dico

        if DevelopmentMode:
            if str(results):
                logger.info('\nRESULTS\n' + str(results))
            else:
                logger.info('\nNO RESULT\n')

        return retour

class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
