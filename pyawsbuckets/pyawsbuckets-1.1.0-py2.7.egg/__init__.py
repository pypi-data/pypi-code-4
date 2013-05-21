from base64 import b64encode
import datetime
from hashlib import md5, sha1
import hmac
import time
import urllib

import httplib2

from exceptions import AwsRequestFailureError


def _request_host(bucket_name):
    return '{bucket_name}.s3.amazonaws.com'.format(
        bucket_name=bucket_name)


class AwsInterface(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    def put(self, protocol, bucket_name, object_name, content,
            content_type=None, server_side_encryption=False):
        """
        PUT content into bucket_name using object_name

        The bucket must already exist at S3.

        """
        if protocol not in ('http', 'https'):
            message = 'invalid protocol: "{protocol}"'.format(
                protocol=protocol)
            raise ValueError(message)

        if content_type is None:
            content_type = ''

        request_host = _request_host(bucket_name)
        self.request_datetime = datetime.datetime.utcnow()
        content_md5 = b64encode(md5(content).digest())
        request_timestamp = self.request_datetime.strftime(
            '%a, %e %b %Y %H:%M:%S +0000')

        headers = [('Host', request_host), ('Date', request_timestamp),
                   ('Content-Length', str(len(content))),
                   ('Content-MD5', content_md5)]
        if content_type:
            headers.append(('Content-Type', content_type))
        headers.append(('Expect', '100-continue'))

        amz_headers = [('x-amz-acl', 'private')]
        if server_side_encryption:
            amz_headers.append(
                ('x-amz-server-side-encryption', 'AES256'))

        signature = self._generate_signature(
            aws_secret_access_key=self._aws_secret_access_key,
            bucket_name=bucket_name,
            object_name=object_name,
            http_verb='PUT',
            request_timestamp=request_timestamp,
            content_md5=content_md5,
            content_type=content_type,
            amz_headers=amz_headers)

        authentication = 'AWS {access_key_id}:{signature}'.format(
            access_key_id=self._aws_access_key_id,
            signature=signature)
        headers.append(('Authorization', authentication))
        headers = tuple(headers) + tuple(amz_headers)

        http_obj = httplib2.Http()
        (resp, body) = http_obj.request(
            '{protocol}://{request_host}{object_name}'.format(
                protocol=protocol,
                request_host=request_host,
                object_name=urllib.quote(object_name)),
            'PUT',
            body=content,
            headers=dict(headers))

        if resp['status'] != '200':
            message = ('Did not receive 200 in status: resp "{resp}" body '
                       '"{body}"'.format(resp=resp,
                                         body=body))
            raise AwsRequestFailureError(message)

        return resp['status']

    def delete(self, bucket_name, object_name):
        request_host = _request_host(bucket_name)

        self.request_datetime = datetime.datetime.utcnow()

        request_timestamp = self.request_datetime.strftime(
            '%a, %e %b %Y %H:%M:%S +0000')

        headers = [('Host', request_host), ('Date', request_timestamp),
                   ('Content-Length', '0')]

        signature = self._generate_signature(
            aws_secret_access_key=self._aws_secret_access_key,
            bucket_name=bucket_name,
            object_name=object_name,
            http_verb='DELETE',
            request_timestamp=request_timestamp)

        authentication = 'AWS {access_key_id}:{signature}'.format(
            access_key_id=self._aws_access_key_id,
            signature=signature)
        headers.append(('Authorization', authentication))
        headers = tuple(headers)

        http_obj = httplib2.Http()
        (resp, body) = http_obj.request(
            'http://{request_host}{object_name}'.format(
                request_host=request_host,
                object_name=urllib.quote(object_name)),
            'DELETE',
            headers=dict(headers))

        if resp['status'] != '204':
            message = ('Did not receive 204 in status: resp "{resp}", body '
                       '"{body}"'.format(resp=resp,
                                         body=body))
            raise AwsRequestFailureError(message)

        return resp['status']

    def sign_object_request(self, protocol, bucket_name, object_name,
                            expiry_minutes):
        """Generate a fixed-life access signature for a private S3 object."""

        expires_epoch = (int(time.mktime(
            datetime.datetime.now().timetuple())) + expiry_minutes * 60)

        signature = urllib.quote(
            self._generate_signature(
                aws_secret_access_key=self._aws_secret_access_key,
                bucket_name=bucket_name,
                object_name=object_name,
                http_verb='GET',
                request_timestamp=str(expires_epoch)))

        # Prepare the return values
        request_host = _request_host(bucket_name)

        uri = (
            '{protocol}://{request_host}{object_name}'
            '?AWSAccessKeyId={aws_access_key_id}'
            '&Expires={expires_epoch}'
            '&Signature={signature}'.format(
                protocol=protocol,
                request_host=request_host,
                object_name=urllib.quote(object_name),
                aws_access_key_id=self._aws_access_key_id,
                expires_epoch=str(expires_epoch),
                signature=signature))
        return {'AWSAccessKeyId': self._aws_access_key_id,
                'Expires': expires_epoch,
                'Signature': signature,
                'uri': uri}

    def _canonicalize_dict(self, dikt):
        """Form concatenated, canonicalized string according to AWS rules."""

        dict_keys = dikt.keys()

        # Zip it up so it's a list where element 0 is a lower-cased key, and
        # element 1 is the original key so get back to the dict with, e.g:
        #   [('content-length', 'Content-Length'), ...]
        canon_key_map = zip([k.lower() for k in dict_keys],
                            dict_keys)

        # Make a list of [(ordered lower case key, value), ...] using the
        # original key to access the value in the original dict.
        canon_list = ['{lower_key}:{value}'.format(
            lower_key=lower_key,
            value=dikt[orig_key]) for (lower_key, orig_key)
            in sorted(canon_key_map)]

        return '\n'.join(canon_list) + '\n'

    def _canonicalize_resource(self, bucket_name, object_name):
        """
        Form canonicalized resource identifier according to the AWS rules.

        """
        return '/{bucket_name}{object_name}'.format(
            bucket_name=bucket_name,
            object_name=urllib.quote(object_name))

    def _build_string_to_sign(self, bucket_name, object_name, http_verb,
                              request_timestamp, content_md5, content_type,
                              amz_headers):
        """
        Build the AWS-defined string to be signed.

        request_timestamp may be either an HTTP format time, or a post-epoch
        seconds 'unix timestamp'.

        """
        # Set Nones to empty strings
        if content_md5 is None:
            content_md5 = ''
        if content_type is None:
            content_type = ''
        if amz_headers is None:
            canon_amz_headers = ''
        else:
            canon_amz_headers = self._canonicalize_dict(dict(amz_headers))
        canon_resource = self._canonicalize_resource(bucket_name, object_name)

        string_to_sign = (
            '{http_verb}\n{content_md5}\n{content_type}\n'
            '{request_timestamp}\n{canon_amz_headers}'
            '{canon_resource}').format(
                http_verb=http_verb,
                content_md5=content_md5,
                content_type=content_type,
                request_timestamp=request_timestamp,
                canon_amz_headers=canon_amz_headers,
                canon_resource=canon_resource).encode('utf-8')

        return string_to_sign

    def _generate_signature(
            self, aws_secret_access_key, bucket_name, object_name, http_verb,
            request_timestamp, content_md5=None, content_type=None,
            amz_headers=None):
        """Generate the AWS Signature string."""

        string_to_sign = self._build_string_to_sign(
            bucket_name=bucket_name,
            object_name=object_name,
            http_verb=http_verb,
            content_md5=content_md5,
            content_type=content_type,
            request_timestamp=request_timestamp,
            amz_headers=amz_headers)

        signature = b64encode(
            hmac.new(
                key=aws_secret_access_key.encode('utf-8'),
                msg=string_to_sign,
                digestmod=sha1).digest())

        return signature
