from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import SubscribeForm


def subscribe(request):
    if request.method == 'POST':
        subscribeForm = SubscribeForm(request.POST)
        if subscribeForm.is_valid():
            if subscribeForm.save():
                return HttpResponseRedirect(reverse('mailchimp:subscribe_success'))
            else:
                return HttpResponseRedirect(reverse('mailchimp:subscribe_failed'))
    else:
        subscribeForm = SubscribeForm()

    return render(request, 'cmsplugin_mailchimp/subscribe.html', {
        'form': subscribeForm,
    })

def unsubscribe(request):
    if request.method == 'POST':
        subscribeForm = SubscribeForm(request.POST)
        if subscribeForm.is_valid():
            if form.save():
                return HttpResponseRedirect(reverse('mailchimp:subscribe_success'))
            else:
                return HttpResponseRedirect(reverse('mailchimp:subscribe_failed'))
    else:
        subscribeForm = SubscribeForm()

    return render(request, 'cmsplugin_mailchimp/subscribe.html', {
        'form': subscribeForm,
    })
