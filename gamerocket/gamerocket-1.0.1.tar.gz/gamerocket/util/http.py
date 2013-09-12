from gamerocket.exceptions.authentication_error import AuthenticationError
from gamerocket.exceptions.authorization_error import AuthorizationError
from gamerocket.exceptions.down_for_maintenance_error import DownForMaintenanceError
from gamerocket.exceptions.not_found_error import NotFoundError
from gamerocket.exceptions.server_error import ServerError
from gamerocket.exceptions.unexpected_error import UnexpectedError
from gamerocket.exceptions.upgrade_required_error import UpgradeRequiredError
from gamerocket import version

import gamerocket
from urllib import urlencode
import json

class Http(object):
    @staticmethod
    def is_error_status(status):
        return status not in [200, 201, 422]
    
    @staticmethod
    def raise_exception_from_status(status, message=None):
        if status == 401:
            raise AuthenticationError()
        elif status == 403:
            raise AuthorizationError(message)
        elif status == 404:
            raise NotFoundError()
        elif status == 426:
            raise UpgradeRequiredError()
        elif status == 500:
            raise ServerError()
        elif status == 503:
            raise DownForMaintenanceError()
        else:
            raise UnexpectedError("Unexpected HTTP_RESPONSE " + str(status))
        
    def __init__(self, config):
        self.config = config
        self.environment = self.config.environment
    
    def post(self, path, params={}):
        return self.__http_do("POST", path, params)
    
    def delete(self, path, params={}):
        return self.__http_do("DELETE", path, params)
    
    def get(self, path, params={}):
        return self.__http_do("GET", path, params)
    
    def put(self, path, params={}):
        return self.__http_do("PUT", path, params)
    
    def __http_do(self, http_verb, path, params=None):
        
        _params = params.copy()

        http_strategy = self.config.http_strategy()
        full_path = self.environment.base_url + self.config.api_version() + path
        
        _params['signature'] = self.config.crypto().sign(http_verb, full_path, _params, self.config.secretKey)
        
        request_body = ''
        if _params != {}:
            request_body = urlencode(_params)
        
        if http_verb == "GET":
            full_path += "?" + request_body
        elif http_verb == "DELETE":
            full_path += "?" + request_body
        
        status, response_body = http_strategy.http_do(http_verb, full_path, self.__headers(), request_body)
                
        if Http.is_error_status(status):
            Http.raise_exception_from_status(status)
        else:
            if len(response_body.strip()) == 0:
                return {}
            else:
                return json.loads(response_body)
    
    def __headers(self):
        return {
            "Accept" : "application/json",
            "Content-type" : "application/x-www-form-urlencoded",
            "User-Agent" : "Gamerocket Python " + version.Version,
            "X-ApiVersion" : gamerocket.configuration.Configuration.api_version()
        }
