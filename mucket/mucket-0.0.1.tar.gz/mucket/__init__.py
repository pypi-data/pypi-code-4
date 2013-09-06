# encoding=utf-8

import re
import httpretty
import hashlib


class Mucket(object):
    """
    Use this class to temporarily mock a whole Boto bucket. Is pretty much
    an S3 mock, except you cannot create buckets, replace or delete objects.
    PUT, GET and HEAD for keys, and GET for buckets.

    >>> from boto import connect_s3
    >>> with Mucket('uglubolli'):
    ...     key = connect_s3().get_bucket('uglubolli').get_key('/bukolli.json')
    ...     key.set_contents_from_string('{a: 1}', {}, replace=True)
    ...     print key.get_contents_as_string()
    ...
    {a: 1}
    >>>

    """

    _bucket_response_xml = \
        """<?xml version="1.0" encoding="UTF-8"?>
        <ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
          <Name>{name}</Name>
          <Prefix/>
          <Marker/>
          <MaxKeys>1000</MaxKeys>
          <IsTruncated>false</IsTruncated>
        </ListBucketResult>
        """

    _supported_official_headers = [
        "cache-control",
        "content-disposition",
        "content-encoding",
        "content-length",
        "content-md5",
        "content-type",
        "expect",
        "expires",
    ]

    def __init__(self, bucket):
        self.bucket_name = bucket
        self.bucket_url = 'https://{}.s3.amazonaws.com/'.format(bucket)
        self.key_url = re.compile(r'https:\/\/{}\.s3\.amazonaws\.com\/[\w\.\-\/\_]+'.format(bucket))
        self.payloads = {}

    def __enter__(self):
        self.mock = not httpretty.is_enabled()
        if self.mock:
            httpretty.enable()

        httpretty.register_uri(httpretty.GET, self.bucket_url,
            body=self._bucket_response_xml.format(name=self.bucket_name),
            content_type='text/plain',
        )

        # Mock S3 key PUT
        httpretty.register_uri(httpretty.PUT, self.key_url, body=self.put_callback)

        # Mock S3 key GET
        httpretty.register_uri(httpretty.GET, self.key_url, body=self.get_callback)

        # Mock S3 key HEAD
        httpretty.register_uri(httpretty.HEAD, self.key_url)

        return self

    def __exit__(self, type, value, traceback):
        if self.mock:
            httpretty.disable()

    def get_callback(self, request, uri, headers):
        resource = self.payloads[uri]
        headers.update(resource['headers'])
        return (200, headers, resource['content'])

    def put_callback(self, request, uri, headers):

        streaming_request = hasattr(request, 'streaming') and request.streaming
        closing_connection = headers.get('connection') == 'close'

        if closing_connection and streaming_request:
            # Closing the connection of a streaming request. No more data
            pass
        elif streaming_request:
            # Streaming request, more data
            self.payloads[uri]['content'] += request.body
        else:
            # Initial data
            # Construct headers
            response_headers = {}
            for header in headers:
                if header.lower() in self._supported_official_headers:
                    response_headers[header] = headers[header]
            self.payloads[uri] = {'content': request.body, 'headers': response_headers}
            request.streaming = True

        etag = hashlib.md5()
        etag.update(self.payloads[uri]['content'])

        headers['etag'] = '"{}"'.format(etag.hexdigest())

        return (200, headers, request.body)
