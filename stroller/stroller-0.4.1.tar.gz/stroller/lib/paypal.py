from urllib import urlencode, unquote
import urllib2, socket

class ResponseWarning(Exception):
    def __init__(self, message):
        self.error_msg = message
        
    def __str__(self):
        return self.error_msg
        
class ResponseError(Exception):
    def __init__(self, message):
        self.error_msg = message
        
    def __str__(self):
        return self.error_msg

class ResponseHandler(object):
    def __init__(self):
        self.tokens = {}
        self.error_messages = []
        
    def parse_response(self, response):
        uri_response = unquote(response.read())
        
        for token in uri_response.split('&'):
            self.tokens[str(token.split("=")[0])] = str(token.split("=")[1])
        
        self.check_success()
        
    def _parse_errors(self):
        i = 0
        while 'L_LONGMESSAGE%s' %i in self.tokens:
            self.error_messages.append(self.tokens['L_LONGMESSAGE%s' %i])
            i += 1
        
    def check_success(self):
        if not self.tokens['ACK'] == 'Success':
            self._parse_errors()
            if self.tokens['ACK'] == 'SuccessWithWarning':
                raise ResponseWarning(self.error_messages[0])
            else:
                raise ResponseError(self.error_messages[0])
                
class PayPal(object):  
    def __init__(self):
        from tg import config
        
        user = config.get('paypal_api_user')
        passwd = config.get('paypal_api_pass')
        development = config.get('paypal_debug', False)
     
        if development:
            self.api_gateway = 'https://api-3t.sandbox.paypal.com/nvp'
            self.api_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
        else:
            self.api_gateway = 'https://api-3t.paypal.com/nvp'
            self.api_url = 'https://www.paypal.com/cgi-bin/webscr'
        
        self.version = '3.2'
        self.signature = config.get('paypal_api_signature')
        self.development = development

        self.account_data = {
        'USER': user,
        'PWD': passwd,
        'VERSION': self.version,
        }

        if self.signature: 
            self.account_data['SIGNATURE'] = self.signature

    def express_checkout_url(self, token):
        return '%s?cmd=_express-checkout&token=%s' % (self.api_url, token)

    def call(self, method, **kw):
        pdict = {}
        for k,v in self.account_data.iteritems():
            pdict[k]=v
        for k,v in kw.iteritems():
            pdict[k.upper()] = v
        pdict['METHOD'] = method
        params = urlencode(pdict)
        
        # If we get here, then the action is valid.  Send it to Paypal
        full_url = "%s?%s" % (self.api_gateway, params)
        if self.development: 
            print full_url
            
        req = urllib2.Request(self.api_gateway, params)

        prevtimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(None)
        request = urllib2.urlopen(req)
        socket.setdefaulttimeout(prevtimeout)
        
        if self.development: 
            print "Request information: %s\n" % request.info()
            
        response_handler = ResponseHandler()
        try:
            response_handler.parse_response(request)
        except ResponseWarning:
            print "TX was successful, but had warnings\n"
        except ResponseError, e:
            raise e
            
        if self.development: 
            for item in response_handler.tokens.keys():
                print "%s: %s" % (item, unquote(response_handler.tokens[item]))
                
        return response_handler
