# -*- coding:utf-8 -*-
import utils

from Acquisition import aq_base
from OFS.Image import File
from zExceptions import NotFound

from Products.CMFCore.FSFile import FSFile
from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.content.file import ATFile
from plone.app.linkintegrity.interfaces import IOFSImage
from plone.namedfile.scaling import ImageScale
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from zope.browserresource.file import File as browserresourcefile
from zope.component.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserView
from zope.component import queryUtility

from stxnext.grayscale import log


def transformation_event(event):
    """
    Checks if current default theme is
    meant to be transformed to grayscale
    """
    request = event.request
    portal = getSite()
    if not portal:
        return
    properties_tool = getToolByName(portal, 'portal_properties')
    transformed_themes = properties_tool.site_properties.getProperty('transformed_themes')
    if not transformed_themes:
        return
    skins_tool = getToolByName(portal, 'portal_skins')
    request_varname = skins_tool.request_varname
    if request.get(request_varname):
        selected_skin = request.get(request_varname)
    else:
        selected_skin = skins_tool.getDefaultSkin()
    if selected_skin in transformed_themes:
        GrayscaleTransformations(event)


def GrayscaleTransformations(event):
    """
    Changing the response body by converting
    the images to grayscale and changing the
    css colors definitions to colors from gray
    shades palette
    """
    request = event.request
    response = request.response
    context = request.get('PUBLISHED')
    resp_body = response.getBody()
    resp_body = getattr(context, 'GET', lambda: '')()

    if hasattr(context, 'im_self'):
        context = context.im_self
    if isinstance(context, ImageScale):
        context = context.data
    if hasattr(context, 'context'):
        context = context.context

    content_type = getattr(context, 'content_type', '')
    if callable(content_type):
        content_type = content_type() or ''
    if not content_type:
        content_type = response.headers.get('content-type') or ''

    if isinstance(context, FilesystemFile):
        resp_body = context().read()
        content_type = context.getContentType().split(';')[0]

    filename = getattr(context, 'getId', lambda: False)()
    filename = getattr(context, 'filename', filename)
    if not filename:
        try:
            filename = context.__name__
        except AttributeError:
            return

    images_content_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']

    browser_resource_image = False
    if isinstance(context, browserresourcefile) and \
       context.content_type.split(';')[0] in images_content_types:
        browser_resource_image = True

    if content_type:
        content_type = content_type.split(';')[0].strip()

    if 'javascript' in content_type:
        return

    if isinstance(context, FSImage) or \
       IOFSImage.providedBy(context) or \
       IATImage.providedBy(context) or \
       content_type in images_content_types or \
       browser_resource_image:

        try:
            path = '/'.join(context.getPhysicalPath())
        except AttributeError:
            path = filename

        try:
            resp_body = utils.get_resource(request, response, path)
        except NotFound:
            image_body = resp_body
            if not image_body:
                if hasattr(context, 'data'):
                    image_body = context.data
                elif isinstance(context, FSImage):
                    image_body = context._readFile(True)

            if image_body:
                resp_body = utils.image_to_grayscale(image_body, path)
            else:
                log.debug('Image doesn\'t contain any data: %s' % (path))

            if queryUtility(IResourceDirectory, name=u''):
                utils.store_resource(path, resp_body)

    elif IBrowserView.providedBy(request.get('PUBLISHED')) or \
        content_type in ['text/html', 'text/css'] or \
        isinstance(context, (File, FSFile, ATFile, FSPageTemplate)) and \
            context.content_type.split(';')[0] in ['text/html', 'text/css']:

        if hasattr(aq_base(context), 'data'):
            resp_body = context.data
            if hasattr(resp_body, 'data'):
                resp_body = resp_body.data

        if isinstance(context, FSFile):
            resp_body = context._readFile(0)

        if content_type == 'text/css' or \
           isinstance(context, (File, FSFile, ATFile, FSPageTemplate)) and \
           context.content_type.split(';')[0] == 'text/css':

            try:
                resp_body = utils.get_resource(request, response, filename)
            except (NotFound, AttributeError):
                resp_body = utils.transform_style_properties(resp_body)
                resp_body = utils.transform_css_url(resp_body)
                if queryUtility(IResourceDirectory, name=u''):
                    utils.store_resource(filename, resp_body)
        else:
            if not resp_body:
                rendered_body = utils.render_object_html(context, request)
                if rendered_body:
                    resp_body = rendered_body
            resp_body = utils.add_bodyclass(resp_body)
            resp_body = utils.transform_style_properties(resp_body)
            resp_body = utils.transform_css_url(resp_body)
            resp_body = utils.transform_img_src(resp_body)

    response.setBody(resp_body)
