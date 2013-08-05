#!/usr/bin/env python2.7
#
# Author: Paul D. Eden <paul_eden@byu.edu>
# Created: 2011-12-20
"""
basic script to call a web service passed in.
"""
import os
from optparse import OptionParser

import byu_ws_sdk as oit
from byu_ws_sdk.demo import setup_demo

import credentials


def other_headers_callback(option, value, parser):
    newValue = {}
    if value:
        for pair in value.split(","):
            if ":" in pair:
                key, keyValue = pair.split(":")
                newValue[key] = keyValue
    setattr(parser.values, option.dest, newValue)


def setup_options_and_run():
    usage = "usage: %%prog [options] url_to_call\n%s" % __doc__
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--http-method", help="one of '%s'" % cli_fmt_list(oit.VALID_HTTP_METHODS), default="GET")
    parser.add_option("-b", "--body", help="filename containing the body for the http request.")
    parser.add_option("-e", "--encoding-type",
                      help="one of %s or %s [%s]" % (oit.ENCODING_URL, oit.ENCODING_NONCE, oit.ENCODING_URL),
                      default=oit.ENCODING_URL)
    parser.add_option("-k", "--key-type",
                      help="one of %s or %s [%s]" % (oit.KEY_TYPE_API, oit.KEY_TYPE_WSSESSION, oit.KEY_TYPE_API),
                      default=oit.KEY_TYPE_API)
    parser.add_option("-a", "--actor", help="the actor to proxy for", default=None)
    parser.add_option("--accept", help="the HTTP request's accept header value", default=None)
    parser.add_option("-c", "--content-type", help="the content-type of the http request")
    parser.add_option("-d", "--demo", action="store_true", help="show the http request and response (like in a demo)")
    parser.add_option("-o", "--other-headers",
                      help="add arbitrary headers to the HTTP request using the following format. "
                           "\"key:value[,key2:value2]\"",
                      action="callback", type="string", default={},
                      callback=other_headers_callback)
    parser.add_option("--actor-in-hash", action="store_true",
                      help="Put the actor in the hash (new way), default False.")
    (options, args) = parser.parse_args()
    c = CallWebServiceCLI(parser, options, args)
    c.main()


def cli_fmt_list(l):
    return "', '".join(l)


class CallWebServiceCLI(object):
    def __init__(self, parser, options, args):
        self._optparser = parser
        self._options = options
        self._args = args

    ##########  Private Methods  ##########

    def _validate_args(self):
        if not oit.valid_http_method(self._options.http_method):
            self._optparser.error("--http-method must be one of '%s'." % cli_fmt_list(oit.VALID_HTTP_METHODS))
        if len(self._args) < 1:
            self._optparser.error("The first argument must be the the url of the web service to call.")
        if self._options.body and not os.path.exists(self._options.body):
            self._optparser.error("If specified, the --body must point to a valid file.")
        if not oit.valid_encoding_types(self._options.encoding_type):
            self._optparser.error("--encoding-type must be one of '%s'." % cli_fmt_list(oit.VALID_ENCODING_TYPES))
        if not oit.valid_key_type(self._options.key_type):
            self._optparser.error("--key-type must be one of '%s'." % cli_fmt_list(oit.VALID_KEY_TYPES))
        if not oit.valid_encoding_types(self._options.encoding_type):
            self._optparser.error("--encoding-type must be one of '%s'." % cli_fmt_list(oit.VALID_ENCODING_TYPES))

    def _generate_headers(self, options, requestBody, url):
        headerValue = oit.get_http_authorization_header(credentials.key, credentials.shared_secret,
                                                        options.key_type, options.encoding_type, url, requestBody,
                                                        options.actor, options.content_type,
                                                        options.http_method, demo=self._options.demo,
                                                        actorInHash=self._options.actor_in_hash)
        headers = {"Authorization": headerValue}
        if options.content_type:
            headers["Content-Type"] = options.content_type
        if options.accept:
            headers["Accept"] = options.accept
        headers.update(
            options.other_headers)  # merge otherHeaders into headers (if key conflict, otherHeaders value wins)
        return headers

    ##########  Public Methods  ##########

    def main(self):
        self._validate_args()
        if self._options.demo:
            setup_demo()
        url = self._args[0]
        requestBody = oit.get_body_from_file(self._options.body)

        headers = self._generate_headers(self._options, requestBody, url)
        response, status, headers, response_full = oit.send_ws_request(url, self._options.http_method, requestBody,
                                                                       headers)

        if not self._options.demo:
            print "Status Code:", status
            print "Headers:", ["%s: %s" % (key, headers[key]) for key in headers.keys()]
            print "Response:", oit.get_formatted_response(headers, response)
