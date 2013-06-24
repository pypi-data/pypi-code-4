from socialcomments import PROVIDERS
from django.utils.importlib import import_module

def get_provider_choices():
	for provider in PROVIDERS:
		module, dot, klass = provider.rpartition('.')
		module = import_module(module)
		
		yield (provider, getattr(module, klass).verbose_name)