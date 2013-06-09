# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# nabla                              Copyright (c) 2013 Jose M. Vicente Segura
# ----------------------------------------------------------------------------
""" Simple WSGI web server.
"""


import wsgiref.simple_server
import pyojo



def application(environ, start_response):
    """ WSGI application.
    
        Initialize a pyojo.Request object with environ, and request to get a 
        response. Then start the response with the status and the headers, and 
        finally send the response.
        
        :param environ: dictionary containing environment variables which is 
            filled by the server for each received request from the client.
      
        :param start_response: callback function supplied by the server which 
            will be used to send the HTTP status and headers to the client.
        
        :rtype: iterable
    """
    request = pyojo.Request(environ)        
    response = request.get_response()    
    start_response(request.status, request.get_response_headers())
    return response



class WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    """ Custom handler for development.
    """
    def log_request(self, code='-', size='-'):
        """ Overrides default method for cleaner output.
        """
        if "/static/js" in self.requestline: return
        self.log_message('"%s" %s %s',
                         self.requestline, str(code), str(size))
    


def main():
    """ Start the WSGI server.
        
        It will receive the request, pass it to the application and send the 
        response to the client.
    """
    host = pyojo.Config.ini.get("WEB", "address")
    port = pyojo.Config.ini.get("WEB", "port")
    message = "Starting HTTP server at %s:%s" % (host, port)
    pyojo.log.info("Static files folder is %s", pyojo.Config.www)
    pyojo.log.info(message)
    print message
    httpd = wsgiref.simple_server.make_server(host = host, 
                                              port = int(port), 
                                              app = application, 
                                              handler_class = WSGIRequestHandler)
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pyojo.log.info("HTTP Server stopped.")
        raise


class HTTPD(object):
    """ Create a web server in a separate process.
    """    
    def __init__(self, config=None):
        import multiprocessing
        self.server = multiprocessing.Process(name='httpd', target=main)
        
    def start(self):
        self.server.start()
        return self

    def stop(self):
        self.server.terminate()
        self.server.join()
        



# ----------------------------------------------------------------------------

if __name__ == '__main__': main()

# ----------------------------------------------------------------------------