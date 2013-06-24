from django.conf import settings

PROVIDERS = getattr(settings, 'COMMENTS_PROVIDERS',
	(
		'socialcomments.providers.twitter.TwitterProvider',
		'socialcomments.providers.facebook.FacebookProvider',
		'socialcomments.providers.linkedin.LinkedInProvider',
		'socialcomments.providers.email.EmailProvider'
	)
)