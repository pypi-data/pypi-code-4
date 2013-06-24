from socialcomments import PROVIDERS
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.importlib import import_module
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.cache import never_cache
from django.contrib import messages

@never_cache
def form(request):
	provider = request.method == 'POST' and request.POST.get('provider') or request.GET.get('p')
	if not provider in PROVIDERS:
		return HttpResponse('')
	
	module, dot, klass = provider.rpartition('.')
	remainder, dot, submodule = module.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	obj = klass()
	connected = False
	
	initial = {
		'provider': provider
	}
	
	identity = None	
	if request.session.get('socialcomments.provider.name') == provider:
		identity = request.session.get('socialcomments.provider.identity')
		if identity:
			initial['identity'] = identity['id']
			initial['name'] = identity['display_name']
			initial['website'] = identity['url']
			connected = True
	
	form = obj.get_form(request.POST or None, initial = initial)
	if request.method == 'POST' and form.is_valid():
		if form.cleaned_data.get('post'):
			content_type = ContentType.objects.get(
				pk = request.POST.get('content_type')
			)
			
			content_object = content_type.get_object_for_this_type(
				pk = request.POST.get('object_id')
			)
			
			obj.post(
				content_object,
				request.session['socialcomments.provider.access_token']
			)
		
		return HttpResponse('::OK::')
	
	templates = [
		'socialcomments/form/%s.inc.html' % submodule,
		obj.template
	]
	
	if identity:
		avatar = obj.get_avatar(identity['id'], 16)
	else:
		avatar = None
	
	return TemplateResponse(
		request,
		templates,
		{
			'form': form,
			'provider_name': provider,
			'provider_name_verbose': obj.verbose_name,
			'connected': connected,
			'identity': identity,
			'avatar': avatar
		}
	)

@never_cache
def connect(request):
	provider = request.GET.get('p')
	if not provider in PROVIDERS:
		return HttpResponse('')
	
	module, dot, klass = provider.rpartition('.')
	remainder, dot, submodule = module.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	obj = klass()
	
	request.session['socialcomments.provider.referer'] = request.META.get('HTTP_REFERER')
	request.session.modified = True
	return obj.connect()

@never_cache
def callback(request):
	provider = request.GET.get('p')
	if not provider in PROVIDERS:
		return HttpResponse('')
	
	module, dot, klass = provider.rpartition('.')
	remainder, dot, submodule = module.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	obj = klass()
	
	kwargs = {}
	for key, value in request.GET.items():
		if value:
			kwargs[key] = value
	
	referer = request.session.pop('socialcomments.provider.referer', '/')
	
	try:
		details = obj.finalise_connection(**kwargs)
	except:
		messages.error(request, u'It wasn\'t possible to authenticate you.')
		return HttpResponseRedirect(referer + '#comments')
	
	if not 'access_token' in details and not 'oauth_token' in details:
		raise Exception(details)
		messages.error(request, u'It wasn\'t possible to authenticate you.')
		return HttpResponseRedirect(referer + '#comments')
	
	info = obj.get_identity(details)
	request.session['socialcomments.provider.name'] = provider
	
	request.session['socialcomments.provider.access_token'] = details
	request.session['socialcomments.provider.identity'] = info
	
	request.session.modified = True
	return HttpResponseRedirect(referer + '#comments')

@never_cache
def disconnect(request):
	referer = request.META.get('HTTP_REFERER', '/')
	request.session.pop('socialcomments.provider.referer', None)
	request.session.pop('socialcomments.provider.name', None)
	request.session.pop('socialcomments.provider.access_token', None)
	request.session.pop('socialcomments.provider.identity', None)
	request.session.modified = True
	
	return HttpResponseRedirect(referer + '#comments')