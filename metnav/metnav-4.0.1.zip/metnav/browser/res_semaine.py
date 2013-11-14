# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

class res_semaine(BrowserView):

    def absolute_url(self):
        return (self.context.absolute_url() + '/' + self.__name__).encode('utf-8')

    def annee_semaine(self, year='', template_url='', output='year_list'):
        context = self.context
        mn_tool = getToolByName(context, 'portal_metadataNav')
        mn_props = getToolByName(context, 'portal_properties').metnav_properties

        params_dict = {'XSL':output,
                        'XSL_PARAMS':{'template.url':template_url,
                                    'current.year':year,
                                    'rss.title':"Semaine",
                                    'rss.desc':'Une ressource de la semaine',
                                    'rss.copyright':'Mon établissement',},
                        'COLLATION':'',
                        'OBJECT_TYPE':mn_props.getProperty('OBJET_SEMAINE', '[lom:educational/lom:learningResourceType &= "figure"]'),
                    }

        query = (str(context.xq_semaine_annee_index) % mn_tool.getQueryParams(params_dict, context.REQUEST))

        da = mn_tool.getDA()

        res = da.query(query, object_only=1)
        context.plone_log('as', str(res))
        return str(res)

    def list_semaine(self, year=None, output='table'):
        context = self.context
        mn_tool = getToolByName(context, 'portal_metadataNav')
        mn_props = getToolByName(context, 'portal_properties').metnav_properties

        if year == None:
            year = int(DateTime().year())
        else:
            year = int(year)

        params_dict = {'XSL':output,
                        'XSL_PARAMS':{'rss.title':"Semaine",
                                    'rss.desc':'Les ressources de la semaine',
                                    'rss.copyright':'Mon établissement',},
                        'COLLATION':'',
                        'OBJECT_TYPE':mn_props.getProperty('OBJET_SEMAINE', '[lom:educational/lom:learningResourceType &= "figure"]'),
                        'LIMITS':'[contains(lom:metaMetadata/lom:contribute[lom:role="creator" or lom:role="createur"]/lom:date/lom:dateTime, "%u")]' % (year),
                    }

        query = (str(context.xq_semaine_index) % mn_tool.getQueryParams(params_dict, context.REQUEST))

        da = mn_tool.getDA()

        res = da.query(query, object_only=1)

        return str(res)

