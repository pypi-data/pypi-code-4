from __future__ import print_function
import eligible
import eligible.header
from eligible.errors import AuthenticationError
import os.path
import json
import urllib

    
def request(method, endpoint, params, extension='.json', payload_prep_func=json.dumps):
    if eligible.api_key == None:
       raise AuthenticationError("No API key provided. Set it with `eligible.api_key = 'your-api-key'`.")

    params['api_key'] = eligible.api_key

    if eligible.test == True:
        params['test'] = 'true'

    if 'reference_id' in params.keys():
        endpoint = os.path.join(endpoint, params['reference_id'])
        del params['reference_id']

    endpoint = os.path.join(eligible.api_base, endpoint + extension)

    return method(endpoint, params, eligible.header.headers, payload_prep_func)

def requests_get(endpoint, params, headers, payload_prep_func):
    try:
        response = requests.get(endpoint, params=params, headers=headers)
    except requests.exceptions.HTTPError as e:
        raise eligible.errors.APIError(str(e))
    except (requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException) as e:
        raise eligible.errors.APIConnectionError(str(e))

    if response.status_code != 200:
        handle_api_error(response.text, response.status_code)

    return response.text

def requests_post(endpoint, params, headers, payload_prep_func):
    try:
        try:
            response = requests.post(endpoint, data=bytes(payload_prep_func(params), 'utf-8'), headers=headers)
        except TypeError:
            # Python 2
            response = requests.post(endpoint, data=payload_prep_func(params), headers=headers)

    except requests.exceptions.HTTPError as e:
        raise eligible.errors.APIError(str(e))
    except (requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException) as e:
        raise eligible.errors.APIConnectionError(str(e))

    if response.status_code != 200:
        handle_api_error(response.text, response.status_code)
        
    return response.text

def config_native_get(request_lib, error_lib):
    def native_get(endpoint, params, headers, payload_prep_func):
        request = request_lib.Request('{}?{}'.format(endpoint, string_payload_prep(params)), headers=headers)
        try:
            f = request_lib.urlopen(request, timeout=80)
            response = f.read()
            response_code = f.getcode()
            
            if response_code != 200:
                handle_api_error(response, response_code)

        except error_lib.HTTPError as e:
            raise eligible.errors.APIError(e.reason, e.code)

        except error_lib.URLError as e:
            raise APIConnectionError(str(e.reason))

        else:
            f.close()

        return response
    return native_get

def config_native_post(request_lib, error_lib):
    def native_post(endpoint, params, headers, payload_prep_func):
        try:
            request = request_lib.Request(endpoint, data=bytes(payload_prep_func(params), 'utf-8'), headers=headers)
        except TypeError:
            request = request_lib.Request(endpoint, data=payload_prep_func(params), headers=headers)
        try:
            f = request_lib.urlopen(request, timeout=80)
            response = f.read()
            response_code = f.getcode()
            
            if response_code != 200:
                handle_api_error(response, response_code)

        except error_lib.HTTPError as e:
            raise eligible.errors.APIError(e.reason, e.code)

        except error_lib.URLError as e:
            raise APIConnectionError(str(e.reason))

        else:
            f.close()

        return response
    return native_post

def handle_api_error(response, response_code):
    error_map = {400: eligible.errors.InvalidRequestError("Bad request: {}".format(response), response_code, response),
                 404: eligible.errors.InvalidRequestError("Endpoint not recognised.", response_code, response),
                 401: eligible.errors.AuthenticationError("There was a problem with your API Key.", response_code, response)}

    try:
        raise error_map[response_code]
    except KeyError:
        raise eligible.errors.APIError(response, response_code, response)

# Compatability - allows for no requests and python 2 or 3
try:
    requests = __import__('requests')
    get = requests_get
    post = requests_post
    try:
        string_payload_prep = urllib.urlencode
    except AttributeError:
        # Using Python 3
        string_payload_prep = urllib.parse.urlencode
        
except ImportError:
    print("Requests is not installed so the API library is using urllib as a fallback.",
          "Using requests is highly recommended as urllib does not verify ssl certs.")
    try:
        urllib2 = __import__('urllib2')
    except ImportError:
        # Using python 3 which doesn't have urllib2
        import urllib.request, urllib.error
        get = config_native_get(urllib.request, urllib.error)
        post = config_native_post(urllib.request, urllib.error)
        string_payload_prep = urllib.parse.urlencode
    else:
        # Python 2
        get = config_native_get(urllib2, urllib2)
        post = config_native_post(urllib2, urllib2)
        string_payload_prep = urllib.urlencode
