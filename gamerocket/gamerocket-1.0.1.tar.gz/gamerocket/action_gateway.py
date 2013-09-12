from gamerocket.result.error_result import ErrorResult
from gamerocket.result.successful_result import SuccessfulResult
from gamerocket.exceptions.not_found_error import NotFoundError
from action import Action

class ActionGateway(object):
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def find(self, id):
        if id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().get("/games/" + self.config.apiKey + "/actions/" + id)
        if "action" in response:
            return SuccessfulResult({"action": Action(self.gateway,response["action"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass
    
    def run(self, id, attributes):
        if id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().post("/games/" + self.config.apiKey + "/actions/" + id + "/run", attributes)
        if "data" in response:
            return SuccessfulResult(response)
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass