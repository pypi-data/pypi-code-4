from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View



class HelloWorld(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello World!')

class ExceptionView(View):
    def get(self, request, *args, **kwargs):
        raise Exception('Unhandled view exception')

class NotFoundView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound('Not found')

