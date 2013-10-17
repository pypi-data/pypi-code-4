# -*- coding: utf-8 -*-
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.pdfpeek import interfaces
from collective.pdfpeek.async import get_queue, Job
from collective.pdfpeek.conversion import remove_image_previews

import logging

logger = logging.getLogger('collective.pdfpeek.browser.utils')


def handle_pdf(content):
    return interfaces.IPDFDataExtractor(content)()


def queue_document_conversion(content, event):
    """
    This method queues the document for conversion.
    One job is queued for the jodconverter if required, and for pdfpeek.
    """

    registry = getUtility(IRegistry)
    settings = registry.forInterface(interfaces.IPDFPeekConfiguration)

    if not settings.eventhandler_toggle:
        return

    converter = interfaces.IPDFDataExtractor(content)
    if converter.content_type not in interfaces.ALLOWED_CONVERSION_TYPES:
        queue_image_removal(content)
        return

    # get the queue
    portal = content.portal_url.getPortalObject()
    conversion_queue = get_queue('collective.pdfpeek.conversion_' + portal.id)
    # create a converter job
    converter_job = Job(handle_pdf, content)
    # add it to the queue
    conversion_queue.pending.append(converter_job)
    logger.info("Document Conversion Job Queued")


def queue_image_removal(content):
    """
    Queues the image removal if there is no longer a pdf
    file stored on the object
    """
    portal = content.portal_url.getPortalObject()
    conversion_queue = get_queue('collective.pdfpeek.conversion_' + portal.id)
    removal_job = Job(remove_image_previews, content)
    conversion_queue.pending.append(removal_job)
    logger.info("Document Preview Image Removal Job Queued")
