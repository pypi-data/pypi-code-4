#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2013-10-12
@author: shell.xu
'''
import os, sys, copy, urllib, logging, functools
from base64 import urlsafe_b64encode
import conf, auth, http, httprpc

logger = logging.getLogger('api')

def make_base_url(domain, key):
    if isinstance(key, unicode):
        key = key.encode('utf-8')
    return 'http://%s/%s' % (domain, urllib.quote(key))

class Url(object):

    def __init__(self, url, mac=None):
        self.url, self.mac = url, mac or auth.MAC

    def __repr__(self):
        return self.url

    @classmethod
    def regfop(cls, n=None):
        def recver(func):
            name = n
            if name is None: name = func.__name__
            @functools.wraps(func)
            def action(self, **kw):
                new = copy.copy(self)
                func(new, **kw)
                return new
            setattr(cls, name, action)
        return recver

    def get(self):
        return httprpc.download(self.url)

@Url.regfop()
def private(self, expires=3600):
    self.url = self.mac.get_url(self.url, expires)

@Url.regfop()
def imageexif(self):
    self.url = self.url + '?exif'

imageView_cmds = {
    'mode': lambda o: str(o),
    'width': lambda o: 'w/%d' % o,
    'height': lambda o: 'h/%d' % o,
    'quality': lambda o: 'q/%d' % o,
    'format': lambda o: 'format/%s' % o}
@Url.regfop()
def imageview(self, **kw):
    self.url += "?imageView/" + '/'.join(
        imageView_cmds[k](v) for k, v in kw.iteritems() if k in imageView_cmds)

@Url.regfop()
def imageinfo(self):
    self.url += '?imageInfo'

def deunicode(s, codec='utf-8'):
    if not isinstance(s, unicode): return s
    return s.encode(codec)

def mkuri_stat(bucket, key):
    return "/stat/" + urlsafe_b64encode("%s:%s" % (bucket, deunicode(key)))

def mkuri_remove(bucket, key):
    return "/delete/" + urlsafe_b64encode("%s:%s" % (bucket, deunicode(key)))

def mkuri_move(bucket_src, key_src, bucket_dst, key_dst):
    return "/move/%s/%s" % (
        urlsafe_b64encode("%s:%s" % (bucket_src, deunicode(key_src))),
        urlsafe_b64encode("%s:%s" % (bucket_dst, deunicode(key_dst))))

def mkuri_copy(bucket_src, key_src, bucket_dst, key_dst):
    return "/copy/%s/%s" % (
        urlsafe_b64encode("%s:%s" % (bucket_src, deunicode(key_src))),
        urlsafe_b64encode("%s:%s" % (bucket_dst, deunicode(key_dst))))

class Bucket(object):
    # upload params:
    # 'callbackUrl', 'callbackBody', 'returnUrl',
    # 'returnBody', 'endUser', 'asyncOps'

    def __init__(self, bucket, domain=None, private=False, mac=None):
        if not hasattr(auth, 'MAC') and mac is None:
            raise conf.ErrorBase('access key is empty')
        self.bucket, self.domain = bucket, domain
        self.private = private
        self.mac = mac or auth.MAC
        self.upparams = {}

    def url(self, key):
        if not self.domain:
            raise conf.ErrorBase('domain not set')
        return Url(make_base_url(self.domain, key), self.mac)

    def put_token(self, key, overwrite=False):
        if overwrite:
            scope = '%s:%s' % (self.bucket, key)
        else: scope = self.bucket
        return self.mac.put_token(scope, token=self.upparams)

    def open(self, key, mode, mime='application/octet-stream'):
        if 'w' in mode:
            return httprpc.PutFile(self, key, mime, '+' in mode)
        elif mode == 'r':
            return self.url(key).get()

    def get(self, key):
        f = self.url(key)
        if self.private: f = f.private()
        f = f.get()
        with f:
            if f.getcode() != 200: raise conf.HttpError(f.getcode())
            return f.read()

    def put(self, key, data, mime='text/plain', overwrite=False):
        # TODO: crc?
        # crc32='', check_crc=0,
        fields = {'token': self.put_token(key, overwrite)}
        fields, files = httprpc.gen_put(key, data, fields, mime)
        boundary = '--------' + httprpc.randstr(20)
        return httprpc.call(
            'http://%s/' % conf.UP_HOST,
            httprpc.encode_multipart_form(boundary, fields, files),
            'multipart/form-data; boundary=%s' % boundary)

    def resumable_put(self, key, stream, mime='text/plain',
                      meta=None, params=None, notify=None, overwrite=False):
        return httprpc.ResumablePut(
            self, key, notify, overwrite).put(
            stream, mime, meta, params)

    def put_file(self, key, filepath, check_crc, **kw):
        # if check_crc:
        #     kw['check_crc'] = 1
        #     kw['crc32'] = httprpc.get_file_crc32(filepath)
        fi = os.stat(filepath)
        with open(filepath, 'rb') as fi:
            if fi.st_size > BLOCK_SIZE:
                self.resumable_put(key, fi)
            else: self.put(key, fi)

    # TODO:
    def domains(self):
        pass

    def _list_prefix(self, **ops):
        ops = dict((k, v) for k, v in ops.iteritems() if v)
        ops.update({'bucket': self.bucket})
        return httprpc.call(
                'http://%s/list?%s' % (conf.RSF_HOST, urllib.urlencode(ops)),
                signfunc=self.mac.sign_req)

    def list_prefix(self, prefix='', marker=None, limit=20):
        while True:
            ret = self._list_prefix(
                prefix=prefix, marker=marker, limit=limit)
            if ret.get('items'):
                for item in ret['items']: yield item
            marker = ret.get('marker')
            if marker is None: break

    def listdir(self, pattern, listfunc=None, **kw):
        import re, fnmatch
        if listfunc is None: listfunc = self.list_prefix
        try:
            index = min(
                filter(
                    lambda i: i != -1,
                    (pattern.find(c) for c in ('.', '*', '[', ']'))))
        except ValueError: index = -1
        prefix = pattern if index == -1 else pattern[:index]
        re_pattern = re.compile(fnmatch.translate(pattern))
        logger.debug('pattern "%s" exp "%s" prefix "%s".' % (
            pattern, re_pattern.pattern, prefix))
        return (f for f in listfunc(prefix, **kw) if re_pattern.match(f['key']))

    def batch(self, ops):
        form = {'op': ops}
        body = []
        for k, v in form.iteritems():
            if not hasattr(v, '__iter__'):
                body.append('%s=%s' % (k, v))
            else: body.extend('%s=%s' % (k, i) for i in v)
        body = '&'.join(body)
        return httprpc.call(
            'http://%s/batch' % conf.RS_HOST, body,
            'application/x-www-form-urlencoded', len(body),
            signfunc=self.mac.sign_req)

    def getstat(self, key):
        return httprpc.call(
            'http://%s%s' % (conf.RS_HOST, mkuri_stat(self.bucket, key)),
            signfunc=self.mac.sign_req)

    def getstats(self, keys):
        rets = self.batch(mkuri_stat(self.bucket, key) for key in keys)
        for i in rets: yield i['code'], i['data']

    def remove(self, key):
        return httprpc.call(
            'http://%s%s' % (conf.RS_HOST, mkuri_remove(self.bucket, key)),
            signfunc=self.mac.sign_req)

    def removes(self, keys):
        rets = self.batch(mkuri_remove(self.bucket, key) for key in keys)
        rets = [(r['code'], e)
                for r, e in zip(rets, keys) if r['code'] != 200]
        if rets: raise conf.BatchError('rename error', rets)

    def copy(self, src, dst, bucket_dst=None):
        if bucket_dst is None: bucket_dst = self.bucket
        return httprpc.call(
            'http://%s%s' % (conf.RS_HOST, mkuri_copy(self.bucket, src, bucket_dst, dst)),
            signfunc=self.mac.sign_req)

    def copys(self, entries, bucket_dst=None):
        if bucket_dst is None: bucket_dst = self.bucket
        rets = self.batch(mkuri_copy(self.bucket, key_src, bucket_dst, key_dst)
                          for key_src, key_dst in entries)
        rets = [(r['code'], e)
                for r, e in zip(rets, entries) if r['code'] != 200]
        if rets: raise conf.BatchError('rename error', rets)

    def rename(self, src, dst, bucket_dst=None):
        if bucket_dst is None: bucket_dst = self.bucket
        return httprpc.call(
            'http://%s%s' % (conf.RS_HOST, mkuri_move(self.bucket, src, bucket_dst, dst)),
            signfunc=self.mac.sign_req)

    def renames(self, entries, bucket_dst=None):
        if bucket_dst is None: bucket_dst = self.bucket
        rets = self.batch(mkuri_move(self.bucket, key_src, bucket_dst, key_dst)
                          for key_src, key_dst in entries)
        rets = [(r['code'], e)
                for r, e in zip(rets, entries) if r['code'] != 200]
        if rets: raise conf.BatchError('rename error', rets)
