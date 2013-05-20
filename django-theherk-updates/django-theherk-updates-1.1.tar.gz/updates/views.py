from django.shortcuts import render_to_response
from django.template import RequestContext
from updates.models import Update


def index(request):
    updates = Update.objects.all().order_by('-date')[:100]
    return render_to_response(
        'updates/index.html',
        {'updates': updates},
        context_instance=RequestContext(request)
    )
