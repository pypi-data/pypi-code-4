class P3PHeadersMiddleware(object):
    def process_response(self, request, response):
        response['P3P'] = 'CP="CAO PSA OUR"'
        return response
