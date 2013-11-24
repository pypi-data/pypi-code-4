class EarlyResponseException(Exception):
    def get_response(self, request):
        return self.args[0]




