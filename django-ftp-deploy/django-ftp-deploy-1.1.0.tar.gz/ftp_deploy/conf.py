from django.conf import settings


BITBUCKET_SETTINGS = getattr(settings, 'DEPLOY_BITBUCKET_SETTINGS', {
    'username' 		: '',
    'password' 		: '',
})


DEPLOY_NOTIFICATIONS = getattr(settings, 'DEPLOY_NOTIFICATIONS', {
   'success':{
        'emails' : [],
        'deploy_user' : True,
        'commit_user' : True
    },
    'fail':{
        'emails' : [],
        'deploy_user' : True,
        'commit_user' : False
    }
})

