#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import lxml.html

from urlparse import urlparse
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zopyx.authoring import authoringMessageFactory as _
from zopyx.smartprintng.plone import xpath_query
from zopyx.smartprintng.plone.browser.images import resolveImage, existsExternalImageUrl

from image import getImageValue


class DebugView(BrowserView):

    _soup = None

    @property
    def soup(self):
        view = self.context.getContentFolder().restrictedTraverse('@@asHTML')
        return lxml.html.fromstring(view())

    def _allRootDocuments(self):
        """ Returns an iterator for all root documents.
            The iterator returns a tuple 
            (document_root_in_zodb, Beautifulsoup node of this document)
        """

        ref_catalog = getToolByName(self.context, 'reference_catalog')
        for div in self.soup.xpath('//div'):
            if 'level-0' in div.get('class', ''):
                div_obj = ref_catalog.lookupObject(div.get('uid'))
                yield div_obj, div

    def debugLevels(self):
        """ return the used Hx level tags """

        result = list()
        for obj, soup in self._allRootDocuments():
            last_level = 1
            headings = []
            for node in soup.xpath(xpath_query(('h1', 'h2', 'h3', 'h4', 'h5', 'h6'))):
                level = int(node.tag[-1])

                error = level > last_level and level-last_level > 1
                headings.append(dict(tag=node.tag, 
                                     level=level,
                                     error=error,
                                     text=node.text_content()))
                last_level = level

            result.append(dict(id=obj.getId(), 
                               title=obj.Title(), 
                               description=obj.Description(), 
                               url=obj.absolute_url(), 
                               heading=headings))
        return result


    def debugLinks(self):
        """ Return a list of links found in the contents document """ 

        links = []
        for document, div in self._allRootDocuments():
            links_in_doc = list()
            for link in div.xpath('//a'): 
                href = link.get('href')
                if not href:
                    continue
                parts = urlparse(href)
                if parts.scheme in ('http', 'https', 'ftp'):
                    css_class = link.get('class', '')
                    if not 'editlink' in css_class:
                        links_in_doc.append(dict(text=link.text_content(),
                                                 css_class=css_class,
                                                 href=href))

            if links_in_doc:                        
                links.append(dict(id=document.getId(),
                                  title=document.Title(),
                                  href=href,
                                  description=document.Description(),
                                  url=document.absolute_url(),
                                  links=links_in_doc))
        return links

    def debugAnchors(self):
        """ Return a list of anchors found in the contents document """ 

        # find all internal linkable objects first (having an 'id' attribute)
        link_ids = [node.get('id') for node in self.soup.xpath('//*') if node.get('id')]

        links = []
        # now check all internal links if they are resolvable or not
        for document, div in self._allRootDocuments():
            links_in_doc = list()
            for link in div.xpath('//a'): 
                href = link.get('href')
                if not href:
                    continue

                ref_id = None
                if href.startswith('resolveuid') and '#' in href:
                    ref_id = href.rsplit('#')[-1]
                elif href.startswith('#'):
                    ref_id = href[1:] # chop of leading '#'
                
                if ref_id:
                    if ref_id in link_ids:
                        links_in_doc.append(dict(text=link.text_content(),
                                                 found=True))
                    else:
                        links_in_doc.append(dict(text=link.text_content(),
                                                 found=False))

            links.append(dict(id=document.getId(),
                              title=document.Title(),
                              href=href,
                              description=document.Description(),
                              url=document.absolute_url(),
                              links=links_in_doc))
        return links

    def debugImages(self):
        """ Return a list of image data for all images inside a content folder """

        result = list()
        images_seen = list()
        for document, document_node in self._allRootDocuments():
            for img in document_node.xpath('//img'):
                src = str(img.get('src'))
                img_obj = resolveImage(document, src)
                if src in images_seen:
                    continue
                images_seen.append(src)
                if img_obj:
                    result.append(dict(id=img_obj.getId(),
                                       obj=img_obj,
                                       title=img_obj.Title(),
                                       uid=img_obj.UID(),
                                       description=img_obj.Description(),
                                       href=img_obj.absolute_url(),
                                       image_src=src,
                                       external_image=False,
                                       pdfScale=getImageValue(img_obj, 'pdfScale'),
                                       excludeFromEnumeration=getImageValue(img_obj, 'excludeFromImageEnumeration'),
                                       linkToFullScale=getImageValue(img_obj, 'linkToFullScale'),
                                       displayInline=getImageValue(img_obj, 'displayInline'),
                                       captionPosition=getImageValue(img_obj, 'captionPosition'),
                                       ))
                else:
                    image_exists = existsExternalImageUrl(src)
                    result.append(dict(id=None,
                                       obj=None,
                                       title=None,
                                       image_exists=image_exists,
                                       uid=None,
                                       description=None,
                                       href=None,
                                       image_src=src,
                                       external_image=True,
                                       pdfScale=None,
                                       excludeFromEnumeration=None,
                                       linkToFullScale=None,
                                       displayInline=None,
                                       captionPosition=None,
                                       ))

        return result

    def updateImages(self):
        """ Update image properties for given set of images by their UID """

        params = self.request.form
        sync_title_description = self.request.form.get('sync_title_description')
        ref_catalog = getToolByName(self.context, 'reference_catalog')
        for uid in params.get('uids', []):
            img = ref_catalog.lookupObject(uid)
            for k,v in params.items():
                field = img.getField(k)
                if field and v != '':
                    img.getField(k).set(img, v)

            if sync_title_description:
                img.setDescription(img.Title())
                img.reindexObject()

        self.context.plone_utils.addPortalMessage(_(u'Image properties updated'))
        return self.request.response.redirect(self.context.absolute_url() + '/@@debug-images')

    def preflightResults(self):
        """ Run an PDF export in preflight mode """

        view = self.context.restrictedTraverse('@@generate_pdf')
        transformations = ['makeImagesLocal']
        return view(transformations=transformations, preflight_only=True)
