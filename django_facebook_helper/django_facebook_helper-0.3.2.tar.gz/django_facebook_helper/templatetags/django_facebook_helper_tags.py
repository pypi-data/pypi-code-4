# -*- coding: utf-8 -*-

from django import template
import urllib
from django.core.urlresolvers import reverse

register = template.Library()
from django.conf import settings

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict

@register.simple_tag(takes_context=True)
def facebook_feed_url(context, friend, link, picture, name, caption, description, action_name, action_link, redirect_uri):
    """
        Direct URL Example
        
        You can also bring up a Feed Dialog by explicitly directing people to the /dialog/feed endpoint:
        
        https://www.facebook.com/dialog/feed?
          app_id=458358780877780&
          link=https://developers.facebook.com/docs/reference/dialogs/&
          picture=http://fbrell.com/f8.jpg&
          name=Facebook%20Dialogs&
          caption=Reference%20Documentation&
          description=Using%20Dialogs%20to%20interact%20with%20users.&
          redirect_uri=https://mighty-lowlands-6381.herokuapp.com/
        
        Click here to try the url yourself. The user will see a dialog that looks like the following:
        
        If a person clicks "Share", the browser will redirect to
        
        https://mighty-lowlands-6381.herokuapp.com/?post_id=12345
        
        The published story will look like this:
        
        If the user clicks "Cancel", the browser will redirect to
        
        https://mighty-lowlands-6381.herokuapp.com/
    """
    
    facebook_app_id = settings.FACEBOOK_APP_ID
    
    param_dict = {
      'app_id': facebook_app_id,
      'link': link,
      'picture': picture,
      'name'  : name,
      'caption': caption,
      'description' : description,
      'redirect_uri': redirect_uri,      
      'to': friend,
      'display' : 'popup',
    }
    
    if action_name != '' and action_link != '':
        param_dict['actions']="[{name:'%s',link:'%s'}]" % (action_name,action_link)
    
    params = urllib.urlencode(encoded_dict(param_dict))
    
    
    return "https://www.facebook.com/dialog/feed?%s" % params
    
    
#     return "https://www.facebook.com/dialog/feed?app_id=%s&to=%s&actions=[{name:'%s',link:'%s'}]&link=%s&picture=%s&name=%s&caption=%s&description=%s&redirect_uri=%s&display=popup" % (
#                         facebook_app_id, friend, action_name, action_link, link, picture, name, caption, description, redirect_uri)
# from django_facebook_helper.templatetags.django_facebook_helper_tags import facebook_feed_url
# facebook_feed_url(226504147430937, 1273360443, None, None, "A Bear Named Winnie (TV)", None, None, None, None, "http://local.filmsobsession.com:8000/facebook-management/facebook-redirect/")
# https://www.facebook.com/dialog/feed?app_id=226504147430937&to=1273360443&actions=[{name:'Comprar%20Pelicula',link:'https://www.google.es'}]&link=http://apps.facebook.com/filmsobsession/movies/detail/a-20-millas-de-la-justicia-a-veinte-millas-de-la-justicia/&picture=http://fo.dev.binomia.es/media/images/movies/W/what_doesn_t_kill_you.jpg&name=A%2020%20millas%20de%20la%20justicia%20(A%20veinte%20millas%20de%20la%20justicia)&caption=filmsobsession.com&description=Una%20organizaci%C3%B3n%20mafiosa%20se%20dedica%20a%20introducir%20inmigrantes%20en%20EE.UU,%20burlando%20a%20la%20polic%C3%ADa%20fronteriza.%20Un%20d%C3%ADa%20dicha%20organizaci%C3%B3n%20comete%20un%20error%20y%20asesina%20a%20sangre%20fr%C3%ADa%20a%20uno%20de%20los%20polic%C3%ADas.%20Charles%20Bronson%20encarna%20a%20un%20duro%20y%20curtido%20polic%C3%ADa%20que%20remover%C3%A1%20cielo%20y%20tierra%20para%20vengar%20la%20muerte%20de%20su%20compa%C3%B1ero.%20&redirect_uri=http://local.filmsobsession.com:8000/facebook-management/facebook-redirect/&display=popup




@register.simple_tag(takes_context=True)
def facebook_request_app_install(context,redirect_uri):
    """
        Este tag genera el enlace para recomendar la app a un amigo 
        
        Direct URL Example
        
        This example uses the the raw URL to render a Request Dialog for your app.
        One key difference from using this method over the JavaScript SDK is the 
        requirement of the redirect_uri parameter.
        
        https://www.facebook.com/dialog/apprequests?
          app_id=APP_ID&
          message=Facebook%20Dialogs%20are%20so%20easy!&
          redirect_uri=http://www.example.com/response
        
        After the user follows the flow and sends the request the browser will redirect to
        
        http://example.com/response?request=REQUEST_ID&to=ARRAY_OF_USER_IDS
        
        If there are errors, the browser will redirect to
        
        http://example.com/response?error_code=ERROR_CODE&error_msg=ERROR_MSG
    """
    facebook_app_id = settings.FACEBOOK_APP_ID
    facebook_app_message = settings.FACEBOOK_APP_INSTALL_MESSAGE
    
    params = urllib.urlencode({
      'app_id': facebook_app_id, 
      'message': facebook_app_message, 
      'redirect_uri'  : redirect_uri,
    })
    
    return u"https://www.facebook.com/dialog/apprequests?%s" % params
