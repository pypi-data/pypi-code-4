from facebook import parse_signed_request
from django.contrib import auth
from django.conf import settings

import logging


logger = logging.getLogger(__name__)


class SignedRequestMiddleware:
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            #Get signed_request sent by facebook
            signed_request = request.POST["signed_request"]
            #Decode of singed request with the FACEBOOK_APP_SECRET
            parsed_request = parse_signed_request(signed_request, settings.FACEBOOK_APP_SECRET)
            
            if parsed_request is False:
                return
                      
            #Avoid CSRF comprobation.
            view_func.csrf_exempt = True
            
            logger.debug("signed_request: %s" % signed_request)
            logger.debug("parsed_request: %s" % parsed_request)
                    
            #Try to authenticate the user with the authbackends
            #Eventually the backend django_facebook_helper.FacebookBackend will authenticate this User
            user = auth.authenticate(token=parsed_request["oauth_token"])
            logger.debug("user: %s" % user)
                  
            
            
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    # Redirect to a success page.
                else:
                    pass # Return a 'disabled account' error message
            else:
                # Return an 'invalid login' error message.
                pass
        except:
            pass

