def link(request, path):
  """return a permalink"""
  base_url = request.application_url.rstrip('/')
  if not path:
    return base_url + '/'
  if not isinstance(path, basestring):
    path = '/'.join(path)
  return '%s/%s' % (base_url, path.lstrip('/'))
  
