from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .forms import InboxSMSForm


@require_POST
def sms_response(request):
    form = InboxSMSForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse('OK')
    else:
        return HttpResponse('Error')
