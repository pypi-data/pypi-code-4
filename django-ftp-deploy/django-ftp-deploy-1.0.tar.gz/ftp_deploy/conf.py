from django.conf import settings


BITBUCKET_SETTINGS = getattr(settings, 'DEPLOY_BITBUCKET_SETTINGS', {
	'username' 		: '',
	'password' 		: '',
	'branch' 		: '',
})

FTP_SETTINGS = getattr(settings, 'DEPLOY_FTP_SETTINGS', {
	'host' 		: '',
	'username' 	: '',
	'password'  : '',
	'path' 		: '',
})

DEPLOY_SECRET_KEY = getattr(settings, 'DEPLOY_SECRET_KEY', '')