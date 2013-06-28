from functools import partial
from hashlib import md5
from tempfile import mkdtemp
import base64
import gzip
import logging
import mimetypes
import os
import pkg_resources
import re

from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from flask import current_app, request, url_for as _url_for
from werkzeug import routing


logger = logging.getLogger(__name__)


CSS_URL_PATTERN = re.compile('url\((?:\'|")?([^\'"\)]+)(?:\'|")?\)')


class S3UrlBuilder(object):

  def __init__(self, access_key_id, secret_access_key, bucket_name,
               key_prefix, cdn_host):
    self._access_key_id = access_key_id
    self._secret_access_key = secret_access_key
    self._bucket_name = bucket_name
    self._key_prefix = key_prefix or ''
    self._cdn_host = cdn_host
    self._calling_format = OrdinaryCallingFormat()
    self._memo = {}
    self._conn = S3Connection(self._access_key_id, self._secret_access_key)

  def build(self, path, protocol='http'):
    path = self._key_prefix + path
    if self._cdn_host:
      return "%s://%s/%s" % (protocol, self._cdn_host, path)
    else:
      return self._calling_format.build_url_base(
        self._conn,
        protocol,
        S3Connection.DefaultHost,
        self._bucket_name,
        path,
      )


class Upstatic(object):

  _compiled_paths = {}
  _roots = {}

  def __init__(self, app=None):
    if app:
      self.init_app(app)
    self._app = app

  @property
  def app(self):
    return self._app or current_app

  @property
  def use_local(self):
    return (self.app.config.get('UPSTATIC_DEBUG_USE_LOCAL', True) and
            self.app.config.get('DEBUG'))

  def _get_md5(self, data, salt=''):
    return base64.urlsafe_b64encode(md5(salt + data).digest())

  def _is_image(self, filename):
    mimetype = mimetypes.guess_type(filename)[0]
    return mimetype and mimetype.startswith('image')

  def _get_compiled_path(self, path, is_gzip, protocol, compiled_data=None):
    compiled_data = compiled_data or self._compile(path, is_gzip, protocol)
    key = "%s\0%s\0%s" % (path, is_gzip, protocol)
    compiled_path = self._compiled_paths.get(key)
    if not compiled_path:
      basename = os.path.basename(path)
      md5 = self._get_md5(compiled_data)
      if self._is_image(basename):
        compiled_path = '/'.join(('c', md5[:1], md5[1:7], basename))
      elif is_gzip:
        compiled_path = '/'.join(('c', md5[:1], md5[1:7], 'gz', basename))
      else:
        compiled_path = '/'.join(('c', md5[:1], md5[1:7], 'raw', basename))
      self._compiled_paths[key] = compiled_path
    return compiled_path

  def _css_replace_url(self, path, is_gzip, protocol, match):
    url = match.group(1).rsplit('#', 1)[0].rsplit('?', 1)[0]
    if url.startswith('http'):  # absolute url
      return url
    elif url.startswith('/'):  # from root
      return url
    else:  # relative to the CSS
      _path = os.path.join(os.path.dirname(path), url)
      _compiled_path = self._get_compiled_path(
        _path,
        is_gzip,
        protocol,
      )
      return "url('%s')" % self.url_builder.build(_compiled_path, protocol)

  def _compile(self, path, is_gzip, protocol):
    try:
      with open(path) as f:
        contents = f.read()
    except IOError:
      return ''
    ext = os.path.splitext(path)[1].lower()
    if ext == '.css':
      css_replace_url = partial(
        self._css_replace_url,
        path,
        is_gzip,
        protocol,
      )
      return CSS_URL_PATTERN.sub(css_replace_url, contents)
    else:
      return contents

  def _walk(self, path):
    for dirpath, _dirnames, filenames in os.walk(path):
      for filename in filenames:
        if filename.lower() not in ('.ds_store', 'thumbs.db'):
          yield os.path.join(dirpath, filename)

  def _compile_path(self, path, protocol='http'):
    tmpdir = mkdtemp()

    logger.info("Compile dir: %r", tmpdir)

    compiled = set()
    compiled_gz = set()

    for filename in self._walk(path):

      for is_gzip in True, False:

        if is_gzip and self._is_image(filename):  # Don't gzip images
          continue

        compiled_data = self._compile(filename, is_gzip, protocol)

        compiled_filename = self._get_compiled_path(
          filename,
          is_gzip,
          protocol,
          compiled_data=compiled_data,
        )

        if compiled_filename in compiled | compiled_gz:
          logger.warn(
            "Already compiled: %r -> %r",
            filename,
            compiled_filename,
          )
          continue

        compiled_dirname = os.path.dirname(compiled_filename)

        # Create directories
        try:
          os.makedirs(os.path.join(tmpdir, compiled_dirname))
        except OSError:
          pass

        # Compile
        try:
          output = os.path.join(tmpdir, compiled_filename)
          if is_gzip:
            f = gzip.open(output, 'wb')
            f.write(compiled_data)
            f.close()
          else:
            with open(output, 'wb') as f:
              f.write(compiled_data)

        except Exception:
          logger.error(
            "Failed to compile: %r -> %r",
            filename,
            compiled_filename,
          )
          raise

        else:
          if is_gzip:
            compiled_gz.add(compiled_filename)
          else:
            compiled.add(compiled_filename)
          logger.info(
            "Compiled: %r -> %r",
            filename,
            compiled_filename,
          )

    logger.info("%s compiled and %s gzip'd.", len(compiled), len(compiled_gz))

    return tmpdir, compiled, compiled_gz

  def _upload(self, tmpdir, filename, bucket, headers, key_prefix):
    try:
      key_name = key_prefix + filename
      key = bucket.get_key(key_name)
      if key:
        logger.info("Already exists: %r", filename)
      else:
        key = bucket.new_key(key_name)
        key.set_contents_from_filename(
          os.path.join(tmpdir, filename),
          headers=headers,
        )
        key.set_acl('public-read')

    except Exception:
      logger.error("Failed to upload: %r", filename)
      raise

    else:
      logger.info("Uploaded: %r", filename)
      return True

    return False

  def init_app(self, app):
    self.url_builder = S3UrlBuilder(
      access_key_id=app.config['UPSTATIC_S3_ACCESS_KEY_ID'],
      secret_access_key=app.config['UPSTATIC_S3_SECRET_ACCESS_KEY'],
      bucket_name=app.config['UPSTATIC_S3_BUCKET_NAME'],
      key_prefix=app.config.get('UPSTATIC_S3_KEY_PREFIX', ''),
      cdn_host=app.config.get('UPSTATIC_S3_CDN_HOST'),
    )

  def url_for(self, *args, **kwargs):
    root = self._roots.get(kwargs.pop('root', None))

    if not (args[0].endswith('static') and root):
      return _url_for(*args, **kwargs)

    path = kwargs['filename'].strip('/')

    if self.use_local:
      root_url = root.get('url')
      if root_url:
        url = os.path.join(root_url, path)
      else:
        url = _url_for(*args, **kwargs)
      return url

    # Get headers info
    is_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
    protocol = request.headers.get('X-Forwarded-Proto', 'https')

    # Get compiled path
    compiled_path = self._get_compiled_path(
      os.path.join(root['path'], path),
      is_gzip,
      protocol,
    )

    return self.url_builder.build(compiled_path, protocol)

  def get_data_path(self, base_dir, package_name=None):
    if not package_name:
      return base_dir
    requirement = pkg_resources.Requirement.parse(package_name)
    return pkg_resources.resource_filename(requirement, base_dir)

  def add_root(self, name, static_folder, package_name=None, root_url=None):
    self._roots[name] = dict(
      path=self.get_data_path(static_folder, package_name),
      url=root_url,
    )

  def upload_all(self, *roots, **kwargs):
    protocol = kwargs.get('protocol', 'http')

    for root in roots:
      path = self._roots[root]['path']

      # Compile
      tmpdir, compiled, compiled_gz = self._compile_path(path, protocol)

      s3_conn = S3Connection(
        self.app.config['UPSTATIC_S3_ACCESS_KEY_ID'],
        self.app.config['UPSTATIC_S3_SECRET_ACCESS_KEY'],
      )
      bucket = s3_conn.create_bucket(self.app.config['UPSTATIC_S3_BUCKET_NAME'])
      key_prefix = self.app.config.get('UPSTATIC_S3_KEY_PREFIX') or ''

      headers = {
        'Cache-Control': 'max-age=31556926',  # 1 year
      }

      # Upload
      files_uploaded = 0

      for compiled_filename in compiled:
        headers['Content-Type'] = (
          mimetypes.guess_type(compiled_filename)[0] or
          'application/octet-stream'
        )
        files_uploaded += self._upload(
          tmpdir,
          compiled_filename,
          bucket,
          headers,
          key_prefix,
        )

      # Upload gzip'd
      files_gz_uploaded = 0

      headers['Content-Encoding'] = 'gzip'

      for compiled_filename_gz in compiled_gz:
        headers['Content-Type'] = (
          mimetypes.guess_type(compiled_filename_gz)[0] or
          'application/octet-stream'
        )
        files_gz_uploaded += self._upload(
          tmpdir,
          compiled_filename_gz,
          bucket,
          headers,
          key_prefix,
        )

      logger.info(
        "%r uploaded and %r gzip'd uploaded.",
        files_uploaded,
        files_gz_uploaded,
      )

