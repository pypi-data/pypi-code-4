# -*- coding: utf-8 -*-
from collective.pdfpeek.interfaces import IPDFDataExtractor
from collective.pdfpeek import interfaces
from collective.pdfpeek.conversion import remove_image_previews
from collective.zamqp.interfaces import IProducer
from collective.zamqp.consumer import Consumer
from collective.zamqp.producer import Producer
from plone.app.uuid.utils import uuidToObject
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.interface import Interface

QUEUE_NAME = "collective.pdfpeek.queue"


class IPDFProcessingMessage(Interface):
    """Marker interface for pdf processing  message"""


class PDFProcessingProducer(Producer):
    """Produces PDF processing tasks"""

    connection_id = "superuser"
    serializer = "msgpack"
    queue = QUEUE_NAME
    routing_key = QUEUE_NAME

    durable = True
    auto_delete = True


class PDFProcessingConsumer(Consumer):
    """Consumes PDF processing tasks"""

    connection_id = "superuser"
    marker = IPDFProcessingMessage
    queue = QUEUE_NAME
    routing_key = QUEUE_NAME

    durable = True
    auto_delete = True


def process_message(message, event):
    """Handle messages received through consumer."""
    uuid = message.header_frame.correlation_id
    context = uuidToObject(uuid)

    if message.body.get('remove', False):
        remove_image_previews(context)
    else:
        IPDFDataExtractor(context)()

    # Send ACK
    message.ack()


def zamqp_queue_document_conversion(context, event):
    """This method queues the document for conversion through
       collective.zamqp.
    """

    registry = getUtility(IRegistry)
    settings = registry.forInterface(interfaces.IPDFPeekConfiguration)

    if not settings.eventhandler_toggle:
        return

    kwargs = {}

    converter = interfaces.IPDFDataExtractor(context)
    if converter.content_type not in interfaces.ALLOWED_CONVERSION_TYPES:
        kwargs['remove'] = True

    producer = getUtility(IProducer, name=QUEUE_NAME)
    producer.register()
    producer.publish(kwargs, correlation_id=IUUID(context))
