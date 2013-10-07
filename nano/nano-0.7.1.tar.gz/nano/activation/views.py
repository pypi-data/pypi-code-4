import logging
_LOG = logging.getLogger(__name__)

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse

from nano.activation.models import Key, ActivationKeyError
from nano.activation.forms import ActivationForm

try:
    from django.shortcuts import render
except ImportError:
    from django.template import RequestContext
    from django.shortcuts import render_to_response
    def render(request, *args, **kwargs):
        return render_to_response(context_instance=RequestContext(request), *args, **kwargs)

@login_required
def activate_key(request, template_name='nano/activation/activation_form.html', *args, **kwargs):
    """Activate a key"""

    data = {'form': ActivationForm()}
    if request.method == 'POST':
        form = ActivationForm(data=request.POST)
        if form.is_valid():
            key = form.cleaned_data['key'].lower()
            try:
                result = Key.objects.activate(key, request.user)
            except ActivationKeyError, msg:
                messages.error(request, msg, fail_silently=True)
                _LOG.error(msg)
                raise Http404
            else:
                msg = 'Key "%s" activated successfully' % key
                messages.success(request, msg, fail_silently=True)
                _LOG.info(msg)
                return HttpResponseRedirect(reverse('nano-activation-ok'))
    return render(request, template_name, data)
