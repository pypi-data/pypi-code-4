import json
import httplib2

class Request:
    
    def _request(self, url, data, action, content_type):

        headers = None
        if data:
            data = json.dumps(data)
            headers = {'Content-Type': content_type}
        h = httplib2.Http()
        responseHeaders, content = h.request(url, action, data, headers)
        try:
            response = json.loads(content)
        except:
            response = content
        return responseHeaders, response

    def get(self, url, data=None, content_type='application/json'):
        return self._request(url, data, 'GET', content_type)

    def post(self, url, data=None, content_type='application/json'):
        return self._request(url, data, 'POST', content_type)

    def put(self, url, data=None, content_type='application/json'):
        return self._request(url, data, 'PUT', content_type)

    def delete(self, url, data=None, content_type='application/json'):
        return self._request(url, None, 'DELETE', content_type)
