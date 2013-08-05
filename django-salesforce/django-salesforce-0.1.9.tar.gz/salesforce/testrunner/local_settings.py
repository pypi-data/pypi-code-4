# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'salesforce_testrunner_db',
	},
	'salesforce': {
		'ENGINE': 'salesforce.backend',
		"CONSUMER_KEY" : '3MVG9FS3IyroMOh4vLOfNRhSkfk0EjzAVdCh0rlGkrAEcJuwqpUwZMu_bGXYsYosog3jAuBQ.fxPcko3_6F3v',
		"CONSUMER_SECRET" : '7230885957056046598',
		'USER': 'pchristensen@freelancersunion.org.devops',
		'PASSWORD': 'X7iZ\;k%1q',
		'HOST': 'https://test.salesforce.com',
	},
}

