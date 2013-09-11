from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .forms import SupportForm

def form(request):
    # In case the auth package is not installed
    user = getattr(request, 'user', None)

    if request.method == 'POST':
        form = SupportForm(user, request.POST)
        if form.is_valid():
            if form.send(request=request):
                return HttpResponseRedirect(reverse('supportform-success'))
    else:
        form = SupportForm(user)

    return render(request, 'supportform/form.html', {
        'form': form,
    })

def success(request):
    return render(request, 'supportform/success.html')
