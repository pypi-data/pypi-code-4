# Create your views here.
from django.views.generic import View
from django.http import HttpResponseRedirect
from .middleware import SESSION_KEY_NAME

class SetFullCookie(View):
    value = True

    def get(self, request):
        request.session[SESSION_KEY_NAME] = self.value
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




