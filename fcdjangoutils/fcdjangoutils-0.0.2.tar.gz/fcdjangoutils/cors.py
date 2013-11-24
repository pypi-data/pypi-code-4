import django.http

def cors(fn = None, origins = '*', methods = ['POST', 'GET', 'OPTIONS'], headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept'], credentials = True):
    """Decorator to set Cross Origin Resource Sharing headers and allow a specific view to be used across sites. Very usefull together with json_view.""" 
    def cors(fn):
        def cors(request, *arg, **kw):
            origins2 = origins
            if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
                response = django.http.HttpResponse()
            else:
                response = fn(request, *arg, **kw)
            if origins2 == "*" and credentials and 'HTTP_REFERER' in request.META:
                origins2 = "/".join(request.META['HTTP_REFERER'].split("/")[:3])
            response['Access-Control-Allow-Origin'] = origins2
            if credentials: response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = ', '.join(methods)
            response['Access-Control-Allow-Headers'] = ', '.join(headers)
            return response
        return cors
    if fn is None:
        return cors
    return cors(fn)
