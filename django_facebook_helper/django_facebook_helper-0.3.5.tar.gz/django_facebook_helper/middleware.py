from facebook import parse_signed_request
from django.contrib import auth
from django.conf import settings

import logging
from django.shortcuts import render_to_response


logger = logging.getLogger(__name__)


class SignedRequestMiddleware:
    
    #code from JDL
    def process_request(self, request):
        if request.POST.has_key("signed_request") and \
            not request.POST.has_key("after_splash_screen"):
            return render_to_response('dfh_splash_screen.html', {'post_info':request.POST["signed_request"], 'facebook_main_url':settings.FACEBOOK_APP_URL})
        
        return None   
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        
        #code from JDL
        if not request.POST.has_key("signed_request"):
            return

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

