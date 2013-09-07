""":mod:`niconico_translator` --- Translating comments on Nico Nico Douga
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import locale
import random
import re
import sys
import time

from dns.resolver import query
from lxml.html import document_fromstring
from lxml.html.html5parser import document_fromstring as html5_fromstring
from lxml.etree import fromstring, tostring
from requests import post, request
from waitress import serve
from webob import Request, Response
from webob.multidict import MultiDict

__all__ = 'App', 'main'


# We resolve the hostname of msg.nicovideo.jp using dnspython,
# to workaround the situation that msg.nicovideo.jp refers to 127.0.0.1
# in /etc/hosts file.
API_HOSTNAME = 'msg.nicovideo.jp'
API_IP_ADDRESS = query(API_HOSTNAME)[0].to_text()

HOPPISH_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
    'upgrade'
}


class App(object):
    """Proxy to msg.nicovideo.jp with translation."""

    def __init__(self, language):
        self.language = language

    def __call__(environ, start_response):
        original_request = Request(environ)
        headers = MultiDict(original_request.headers)
        original_request.host = API_IP_ADDRESS
        original_response = request(
            original_request.method,
            original_request.url,
            headers=headers,
            data=original_request.body
        )
        response = Response()
        response.status = original_response.status_code
        response.headers = original_response.headers
        for hop in HOPPISH_HEADERS:
            response.headers.pop(hop, None)
        if has_to_translate(original_request, original_response):
            response.body = translate_response(
                original_response.content,
                self.language
            )
        else:
            response.body = original_response.content
        return response(environ, start_response)


def has_to_translate(request, response):
    """Whether the response has to be translated or not."""
    return (request.method == 'POST' and
            response.headers.get('Content-Type') == 'text/xml')


def translate_response(xml, language):
    """Translate XML response."""
    document = fromstring(xml)
    chats = [chat for chat in document.xpath('//packet/chat')
                  if chat.text and chat.text.strip()]
    translated_chats = translate_multiple(
        (chat.text for chat in chats),
        language
    )
    for chat, translated_chat in zip(chats, translated_chats):
        chat.text = translated_chat
    return tostring(document, encoding='utf-8')


TRANSLATE_API_URL = 'http://translate.google.hu/translate_t'


def translate(text, language):
    """Translate text using Google Translate.
    Referred `Google Translator for Firefox`__ extension.

    __ http://translatorforfirefox.blogspot.com/

    """
    response = post(
        TRANSLATE_API_URL,
        data={
            'text': text,
            'hl': language,
            'langpair': 'auto|' + language,
            'tbb': '1'
        }
    )
    document = document_fromstring(response.content)
    try:
        result = document.get_element_by_id('result_box')
    except (KeyError, IndexError):
        document = html5_fromstring(response.content)
        result = document.xpath('descendant-or-self::*[@id="result_box"]')
        return result[0].xpath('string()')
    else:
        return result.text_content()


LIMITS = [30000, 10000, 5000]


def translate_multiple(text_list, language, limit=30000):
    """Translate many texts at a time."""
    boundary = ' {0} '.format(int(time.time() * random.randrange(1000, 9999)))
    boundary_size = len(boundary)
    buffer = []
    buffer_size = 0
    input_size = 0
    result_list = []
    def _flush_buffer():
        nonlocal buffer, buffer_size, input_size, result_list
        if buffer_size:
            result = translate(''.join(buffer), language)
            sublist = re.split(r'\s*' + boundary.strip() + r'\s*', result)
            sublist_size = len(sublist)
            assert sublist_size == input_size, \
                   'expected {0}, but got {1}'.format(input_size, sublist_size)
            result_list += sublist
            buffer = []
            buffer_size = 0
            input_size = 0
    def flush_buffer():
        try:
            _flush_buffer()
        except AssertionError:
            try:
                _flush_buffer()  # retry
            except AssertionError:
                return False
        return True
    def retry():
        """Retry translation with more thight limit."""
        try:
            next_limit = LIMITS[LIMITS.index(limit) + 1]
        except (IndexError, ValueError):
            assert limit > 1
            next_limit = limit / 2
        return translate_multiple(text_list, language, next_limit)
    for text in text_list:
        text_size = len(text)
        added_size = buffer_size + (buffer_size and boundary_size) + text_size
        if added_size > limit:
            if not flush_buffer():
                return retry()
            added_size = text_size
        if buffer_size:
            buffer.append(boundary)
        buffer.append(text)
        input_size += 1
        buffer_size = added_size
    if not flush_buffer():
        return retry()
    return result_list


def main():
    if len(sys.argv) > 1:
        language = sys.argv[1]
    else:
        language = (locale.getlocale()[0] or 'en')[:2]
    app = App(language)
    serve(app, port=80)


if __name__ == '__main__':
    main()
