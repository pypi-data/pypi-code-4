from socialcomments import PROVIDERS
from django.utils.importlib import import_module

def comments(request):
	def providers():
		active = request.session.get('socialcomments.provider.name')
		request.session.modified = active is not None
		
		for i, provider in enumerate(PROVIDERS):
			module, dot, klass = provider.rpartition('.')
			module = import_module(module)
			klass = getattr(module, klass)
			
			yield {
				'active': (active and active == provider) or (not active and i == 0),
				'name': provider,
				'verbose_name': klass.verbose_name,
				'icon': klass.icon
			}
	
	return {
		'social_comment_providers': providers
	}