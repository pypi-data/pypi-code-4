import eligible.url
from eligible.url import string_payload_prep
from eligible.url import get as GET
from eligible.url import post as POST
from eligible.errors import InvalidRequestError
import os.path
import json
import urllib

            
class Endpoint(object):
    '''
    Defines an endpoint able to initialise a new instance of a class
    upon return of data from API endpoint
    '''
    def __init__(self, method, endpoint, allow_references=False):
        '''Create an Endpoint instance, signifying an endpoint the user can query'''
        self.method = method
        self.endpoint = endpoint
        self.allow_references = allow_references

    def __call__(self, params={}):
        '''Query the endpoint given the attributes set in __init__ and params given'''
        if not self.allow_references and 'reference_id' in params.keys():
            raise InvalidRequestError("{} does not use reference ids.".format(self.endpoint))
        try:
            response = str(eligible.url.request(self.method, self.endpoint, params), 'utf-8')
        except TypeError:
            # Python 2
            response = eligible.url.request(self.method, self.endpoint, params)
        response, response_json = json.loads(response), response
        return self._parent(response, response_json)

    def _set_parent(self, parent):
        '''
        Register 'parent' as the Enpoint's parent class, 
        to return a response type {parent}Response
        '''
        self._parent = parent


class SimpleEndpoint(object):
    '''
    Defines simpler endpoints, such as ones where a plain string will be passed in (X12/SOAP)
    '''
    def __init__(self, method, endpoint, param_name, _payload_prep_func=string_payload_prep):
        '''Create a simple endpoint instance'''
        self.method = method
        self.endpoint = endpoint
        self.param_name = param_name # Permanent param name to go into params hash
        self._payload_prep_func = _payload_prep_func # For non-JSON this will usually be urllib.urlencode/urllib.parse.urlencode, as default

    def __call__(self, param_string):
        '''Use the info passed in upon initialisation to send a simple (string-based) request.'''
        params = {self.param_name: param_string}
        return eligible.url.request(self.method, self.endpoint, params, extension='', payload_prep_func=self._payload_prep_func)


class InstanceBuilder(object):
    '''
    A class which, when given a dict, will return an instance
    which has a __dict__ updated with the elements of the given dict
    '''
    # Necessary to return instances instead of classes.
    def __init__(self, dct):
        '''Update the instance dictionary with the dct argument'''
        self.__dict__.update(dct)


class EndpointRegister(type):
    '''A metaclass which handles registering of Endpoint objects which are class attributes'''
    def __init__(cls, name, bases, dct):
        # You *might* do without this, but having it means that specifying
        # and Endpoint for the resources below is slightly simpler (you'd have to
        # find a way to pass in the class manually otherwise).
        for k, v in dct.items():
            if isinstance(v, Endpoint):
                v._set_parent(cls)
    

class APIResource(object):
    '''APIResorce abstract base class'''
    def __new__(cls, response, response_json):
        '''Build an API Resource for a given response'''
        # Add JSON for each object into its dictionary, and build the new instances
        if type(response) == list:
            # Enrollments return a json list, so map over instead of trying to convert the list
            try:
                for r in response:
                    r['json'] = json.dumps(r)
            except ValueError:
                raise eligible.errors.APIError("Invalid Response Object returned from API: {}".format(response))

            instance_dicts = [cls._build_instance_dict(r) for r in response]
            return [cls._build_instance(d) for d in instance_dicts]
        else:
            try:
                response['json'] = response_json
            except:
                raise eligible.errors.APIError("Invalid Response Object returned from API: {}".format(response))

            instance_dict = cls._build_instance_dict(response)
            return cls._build_instance(instance_dict)


    @classmethod
    def _build_instance(cls, instance_dict):
        '''Build an instance, given a dictionary to use'''
        # Create a type {resource}Response, and use InstanceBuilder to return an instance of it
        return type(cls.__name__ + 'Response', (InstanceBuilder,), {})(instance_dict)

    @staticmethod
    def _build_instance_dict(response_dict):
        '''Build an API resource instance given a dictionary'''
        return response_dict # Default behaviour, does not need to be overridden but should be


APIResource = EndpointRegister('APIResource', (APIResource,), {})


# Resource Definitions
class Acknowledgement(APIResource):
    get = Endpoint(GET, 'claims/acknowledgements', allow_references=True)


class Claim(APIResource):
    post = Endpoint(POST, 'claims')


class Coverage(APIResource):
    get = Endpoint(GET, 'coverage/all')


class Demographic(APIResource):
    get = Endpoint(GET, 'demographic/all')


class Enrollment(APIResource):
    get = Endpoint(GET, 'enrollment')
    post = Endpoint(POST, 'enrollment')


class Payment(APIResource):
    status = Endpoint(GET, 'payment/status', allow_references=True)
    # reports = Endpoint(GET, 'payment/reports', allow_references=True)


# Simple Resources, that send and return strings
class X12(object):
    post = SimpleEndpoint(POST, 'x12', 'X12')
