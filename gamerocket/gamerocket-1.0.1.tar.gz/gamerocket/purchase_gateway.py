from gamerocket.result.error_result import ErrorResult
from gamerocket.result.successful_result import SuccessfulResult
from purchase import Purchase
from gamerocket.exceptions.not_found_error import NotFoundError

class PurchaseGateway(object):
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config
    
    def find(self, id):
        if id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().get("/games/"+ self.config.apiKey + "/purchases/" + id)
        if "purchase" in response:
            return SuccessfulResult({"purchase": Purchase(self.gateway,response["purchase"])})
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass
    
    def buy(self, id, attributes):
        if id == None or id.strip() == "":
            raise NotFoundError()
        response = self.config.http().post("/games/"+ self.config.apiKey + "/purchases/" + id + "/buy", attributes)
        if "data" in response:
            return SuccessfulResult(response)
        elif "error" in response:
            return ErrorResult(response)
        else:
            pass