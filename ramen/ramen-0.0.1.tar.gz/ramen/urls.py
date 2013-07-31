from tornado.util import import_object


def pattern(*args, **kwargs):
    temp = []
    for arg in args:
        if type(arg) == type(()):
            temp.append(arg)
            
        if type(arg) == type([]):
            temp.extend(arg)
        
    return temp
    
def include(prefix, src, namespace = None, extra_params = {}):
    if type(src) == str:
        package = import_object(src)
        patterns = package.patterns
    else:
        patterns = list(src)
    
    temp = []
    for pattern in patterns:
        if len(pattern) == 2:
            path, handler = pattern 
            kwargs = {}            
        if len(pattern) == 3:
            path, handler, kwargs = pattern
        
        #print path, handler, kwargs, namespace

        if extra_params:
            kwargs.update(extra_params)

        if namespace:
            kwargs.setdefault('namespaces', []).insert(0, namespace)
        
        if prefix.startswith('^'):
            _path = path 
            _suffix = ''

            if path.endswith('$'):
                _path = path[:-1]
                _suffix = '$'
                        
            if not (_path.endswith('/?') or _path.endswith('/')):
                _path = '%s/?%s' % (_path, _suffix)
                path = _path

            elif _path.endswith('/') and not _path.endswith('/?'):
                _path = '%s?%s' % (_path, _suffix)
                path = _path

        nkw = dict(kwargs)
        nkw.update(extra_params)

        temp.append(('%s%s' % (prefix, path), handler, nkw))
        
    
    return temp
    
    
