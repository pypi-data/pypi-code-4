# Create your views here.

from django.views.generic import TemplateView


class TestView(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        return self.render_to_response({'object': 'Hello world'})




