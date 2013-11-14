##parameters=encoding='utf-8'
##title=RSS
from Products.CMFCore.utils import getToolByName
MAX_ITEMS       = 10
EXIST           = context.exist                        # Connecteur eXistDA vers la base XML
portal_url = getToolByName(context, 'portal_url') 
portal = portal_url.getPortalObject()
sender = portal.getProperty('email_from_address')
results_exist = container.restrictedTraverse("SearchRecents").searchRecentXMLDocs(fullpath=True)[:MAX_ITEMS]

#from zLOG import LOG, INFO
s_properties=container.portal_properties.site_properties
site_title=portal.getProperty('title')
site_title= site_title.decode('utf-8')

if encoding != s_properties.default_charset:
  selected_charset = encoding
else:
  selected_charset = s_properties.default_charset

retour = """<?xml version="1.0" encoding="%s"?>
<rss version="2.0">
  <channel>
    <title>Les nouveautés de %s</title>
    <link>%s</link>
    <description>Les nouveautés de %s</description>
    <language>fr-fr</language>
    <copyright>école Normale Supérieure de Lyon</copyright>
    <managingEditor>%s</managingEditor>
    <webMaster>%s</webMaster>
    <generator>Plone, eXist</generator>
""" % (selected_charset, site_title, container.portal_url(), site_title, sender, sender)

for res in results_exist:
    auteurs=context.getAuteurs(res.get('res/author', '')[0])
    retour += """
    <item>
      <title>%s</title>
      <link>%s</link>
      <description>%s</description>
      <guid>%s</guid>
      <pubDate>%s</pubDate>""" % (res.get('res/title', '')[0], res.get('res/url', '')[0], res.get('res/description', '')[0], res.get('res/url', '')[0], res.get('res/pubdate', '')[0])
    for auteur in auteurs:
        retour += """ <author>%s</author> """ % auteur
    retour += """</item>"""

container.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
retour = retour + """  </channel>
</rss>"""
if encoding != s_properties.default_charset:
  retour = unicode(retour).encode(selected_charset)
return retour

