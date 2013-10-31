#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2013-10-12
@author: shell.xu
'''
import json, zlib, random, socket, string, cStringIO, logging, threading
from base64 import urlsafe_b64encode
from contextlib import contextmanager
import conf, http

logger = logging.getLogger('rpc')

class SocketPool(object):

    def __init__(self):
        self.lock = threading.RLock()
        self.buf, self.max_buf = {}, conf.getcfg('main', 'max_conn_buf', int, 3)
	self.concur = None
        if conf.getcfg('main', 'max_concurrency'):
            self.concur = threading.BoundedSemaphore(
                conf.getcfg('main', 'max_concurrency', int, 10))
        logger.debug('max conn buff: %d' % self.max_buf)

    def acquire(self, host, port):
        conn, addr = None, (socket.gethostbyname(host), port)
        if self.concur: self.concur.acquire()
        with self.lock:
            if self.buf.get(addr):
                conn = self.buf[addr].pop(0)
                logger.debug('acquire conn %s:%d size %d' % (
                        host, port, len(self.buf.get((host, port)))))
        if conn is None:
            conn = socket.socket()
            conn.connect(addr)
        return conn

    def release(self, conn, keep_alive=False):
        if self.concur: self.concur.release()
        if keep_alive:
            addr = conn.getpeername()
            if addr in self.buf and len(self.buf[addr]) < self.max_buf:
                with self.lock:
                    self.buf.setdefault(addr, [])
                    self.buf[addr].append(conn)
                    logger.debug('release conn %s:%d size %d' % (
                            addr[0], addr[1], len(self.buf.get(addr))))
                if self.concur: self.concur.release()
                return
        conn.close()

spool = SocketPool()

# FIXME: https cert?
# not support proxy!

def download(url):
    logger.debug('download "%s"' % url)
    host, port, uri = http.parseurl(url)
    req = http.request_http(uri)
    req.set_header('Host', host)
    req.set_header('User-Agent', conf.USER_AGENT)
    req.set_header('Connection', 'keep-alive')

    conn = spool.acquire(host, port)
    stream = conn.makefile()
    try:
        req.sendto(stream)
        stream.flush()
        resp = http.recv_msg(stream, http.Response)
        f = resp.makefile()

        real_close = f.close
        def close():
            real_close()
            spool.release(conn, resp.get_header('Connection') == 'keep-alive')
        f.close = close
        return f
    except:
        spool.release(conn)
        raise

def call(url, body=None, content_type=None,
         content_length=None, signfunc=None):
    logger.debug('call "%s" mime "%s"' % (url, content_type))
    host, port, uri = http.parseurl(url)

    req = http.request_http(uri, method='POST', body=body)
    req.set_header('Host', host)
    req.set_header('User-Agent', conf.USER_AGENT)
    req.set_header('Connection', 'keep-alive')
    if content_type:
        req.set_header('Content-Type', content_type)
    if content_length:
        req.set_header('Content-Length', str(content_length))
    if signfunc is not None:
        signfunc(req)

    conn, resp = spool.acquire(host, port), None
    try:
        stream = conn.makefile()
        req.sendto(stream)
        stream.flush()
        resp = http.Response.recv_msg(stream)
        ret = resp.read_body()
    finally:
        spool.release(
            conn, resp is not None and resp.get_header('Connection') == 'keep-alive')
    return response_json(resp, ret)

def response_json(resp, ret):
    if resp.code / 100 == 2:
        try: return json.loads(ret)
        except ValueError: return ret
    try:
        ret = json.loads(ret)
        err = ret['error'] if 'error' in ret else ret
    except ValueError: err = ret
    detail = resp.get_header("X-Log")
    if detail is not None:
        err = conf.HttpRpcError(err, detail)
    else: err = conf.HttpRpcError(err)
    raise err

def qiniu_escape(s):
    return s.replace('\\', '\\\\').replace('\"', '\\\"')

def encode_multipart_form(boundary, fields, files):
    for k, v in fields.iteritems():
        yield '--%s\r\n' % boundary
        yield 'Content-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (k, v)
    for f in files:
        yield '--%s\r\n' % boundary
        yield 'Content-Disposition: form-data; name="file"; filename="%s";\r\n' % \
                         qiniu_escape(f.get('filename'))
        yield 'Content-Type: %s\r\n\r\n' % (
                f.get('content_type') or 'application/octet-stream')
        data = f.get('data')
        if data is None: return
        elif isinstance(data, basestring):
            yield data
        elif hasattr(data, 'read'):
            for d in http.file_source(data): yield d
        elif hasattr(data, '__iter__'):
            for d in data: yield d
        yield '\r\n'
    yield '--%s--\r\n' % boundary

def randstr(n, sets=string.hexdigits):
    return ''.join(random.choice(sets) for i in xrange(n))

def get_file_crc32(filepath):
    crc = 0
    with open(filepath, 'rb') as fi:
        block = fi.read(conf.BLOCK_SIZE)
        while len(block) != 0:
            crc = zlib.crc32(block, crc) & 0xFFFFFFFF
            block = f.read(conf.BLOCK_SIZE)
    return crc

def gen_put(key, data, fields,
            # crc32='', check_crc=0,
            mime='application/octet-stream'):
    for k, v in fields.iteritems():
        fields[k] = str(v)
    # if check_crc:
    #     fields['crc32'] = str(crc32)
    if key is not None:
        fields['key'] = key

    if key is None:
        key = randstr(9, string.ascii_lowercase)
    elif key is '': key = 'index.html'
    return fields, [{'filename': key, 'data': data, 'mime_type': mime},]

class PutFile(http.RequestFile):

    def __init__(self, bucket, key,
                 mime='application/octet-stream', overwrite=False):
        self.boundary = '--------' + randstr(20)
        # TODO: other upload params
        fields = {'token': bucket.put_token(key, overwrite)}
        fields, files = gen_put(key, None, fields, mime)

        logger.debug('put file:', key)
        host, port = conf.UP_HOST, 80
        req = http.request_http('/', method='POST')
        req.set_header('Host', host)
        req.set_header('User-Agent', conf.USER_AGENT)
        req.set_header('Connection', 'keep-alive')
        req.set_header('Transfer-Encoding', 'chunked')
        req.set_header(
            'Content-Type', 'multipart/form-data; boundary=%s' % self.boundary)

        self.conn = spool.acquire(host, port)
        self.stream = self.conn.makefile()
        req.send_header(self.stream)
        self.write(''.join(encode_multipart_form(
                    self.boundary, fields, files)))

    def close(self):
        if hasattr(self, 'rslt'): return
        self.write('\r\n--%s--\r\n' % self.boundary)
        http.RequestFile.close(self)
        resp = self.get_response()
        ret = resp.read_body()
        spool.release(
            self.conn, resp.get_header('Connection') == 'keep-alive')
        self.rslt = response_json(resp, ret)

    def result(self):
        return self.rslt

def gen_chunk(block, chunk_size):
    for i in xrange(0, len(block), chunk_size):
        l = min(len(block) - i, chunk_size)
        yield block[i:i+l]

class ResumablePut(object):

    def __init__(self, bucket, key, notify=None, overwrite=False):
        self.bucket, self.key = bucket, key
        self.overwrite, self.notify = notify, overwrite
        self.ctxs = []

    def sign_req(self, req):
        req.set_header(
            'Authorization',
            'UpToken ' + self.bucket.put_token(self.key, self.overwrite))

    def put(self, f, mime=None, meta=None, params=None):
        offset = 0
        while True:
            # FIXME: read breaked?
            d = f.read(conf.BLOCK_SIZE)
            if not d: break
            self.put_block(offset, d)
            offset += len(d)
        ret = self.mkfile(self.key, size, mime, meta, params)
        return ret['key'], ret['hash']

    def put_block(self, block_offset, block):
        block_size = len(block)
        s = gen_chunk(block, conf.CHUNK_SIZE)

        # FIXME: retry
        chunk = s.next()
        ctx, offset, host = self.mkblock(chunk)
        if self.notify: self.notify(block_offset, offset, ctx)

        while offset < block_size:
            chunk = s.next()
            print 'offset:', offset, 'host:', host
            print 'ctx:', ctx
            ctx, offset, host = self.putblock(chunk, host, ctx)
            if self.notify: self.notify(block_offset, offset, ctx)

        self.ctxs[block_offset / conf.BLOCK_SIZE] = ctx

    def mkblock(self, chunk):
        l = min(len(chunk), conf.BLOCK_SIZE)
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        ret = call(
            "http://%s/mkblk/%s" % (conf.UP_HOST, l), chunk,
            'application/octet-stream', l, signfunc=self.sign_req)
        print ret
        if ret['crc32'] != crc:
            raise conf.ErrorBase('crc not match', ret['crc32'], crc)
        return ret['ctx'], ret['offset'], ret['host']

    def putblock(self, chunk, host, ctx):
        l = min(len(chunk), conf.BLOCK_SIZE)
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        ret = call(
            "%s/bput/%s/%s" % (host, ctx, l), chunk,
            'application/octet-stream', l, signfunc=self.sign_req)
        if blk['crc32'] != crc:
            raise conf.ErrorBase('crc not match', ret['crc32'], crc)
        return ret['ctx'], ret['offset'], ret['host']

    def mkfile(self, key, fsize, mime=None, meta=None, params=None):
        url = ['http://%s/mkfile/%s/key/%s' % (conf.UP_HOST, fsize, urlsafe_b64encode(key)),]
        if mime:
            url.extend(['mimeType', urlsafe_b64encode(mime)])
        if meta:
            url.extend(['meta', urlsafe_b64encode(meta)])
        if params:
            url.extend(['params', urlsafe_b64encode(params)])
        body = ','.join(self.ctxs)
        return call(
            "/".join(url), body, 'text/plain',
            len(body), signfunc=self.sign_req)
