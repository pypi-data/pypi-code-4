from cssocialprofile.models import get_profile_model
from cssocialprofile.utils.load_images import loadUrlImage
from django.conf import settings
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import OpenIDBackend

def get_facebook_photo(response):
    """ """
    import facebook.djangofb as facebook
    
    facebook = facebook.Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_API_SECRET)
    uid = response.get('id')
    user_data = facebook.users.getInfo(uid, ['first_name', 'last_name','pic_big',])[0]
    if user_data:
        img_url = user_data['pic_big']
        img_title = u'Facebook: ' + user_data['first_name'] + u' ' + user_data['last_name']
        return loadUrlImage(img_url,img_title)
    else:
        return None


def get_twitter_photo(response):
    """ """
    img_url = response.get('profile_image_url')
    img_url=img_url.replace('_normal.','.')
    username = response.get('screen_name')
    return loadUrlImage(img_url,u'twitter: ' + username)



def facebook_extra_values(backend, details, response, uid, username, user=None, *args, **kwargs):
    """ """
    if backend.__class__ == FacebookBackend:
        model = get_profile_model()
        profile,new = model._default_manager.get_or_create(user=user) 
        profile.facebook_id = response.get('id')

        if profile.usertype == 0:
            profile.usertype = 1
        
        if profile.added_source == 0:
            #First time logging in
            profile.added_source = 3

        if not profile.fullname:
            profile.fullname = user.first_name + ' ' + user.last_name
            
        if not profile.photo:
            profile.photo = get_facebook_photo(response)
            
        profile.save()


def twitter_extra_values(backend, details, response, uid, username, user=None, *args, **kwargs):
    """ """
    if backend.__class__ == TwitterBackend:
        model = get_profile_model()
        profile,new = model._default_manager.get_or_create(user=user) 

        if not profile.photo:
            profile.photo = get_twitter_photo(response)
        profile.twitter_id = response.get('screen_name','')

        if profile.usertype == 0:
            profile.usertype = 1
        if profile.added_source == 0:
            profile.added_source = 2

        if not profile.bio:
            profile.bio = response.get('description','')         

        if not profile.fullname:
            profile.fullname = response.get('name','')    

        profile.save()

def openid_extra_values(backend, details, response, uid, username, user=None, *args, **kwargs):
    """ """
    if backend.__class__ == OpenIDBackend:
        profile = user.get_profile()

        if response.status == 'success':
            profile.openid_id = response.getDisplayIdentifier()
            if profile.added_source == 0:
                profile.mota = 1
                profile.added_source = 4
        profile.save()
