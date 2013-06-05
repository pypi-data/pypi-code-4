
'''
Generic views for using Serialisers and Publishers
'''
from django.views import generic

class DetailView(generic.DetailView):
    def dispatch(self, request, **kwargs):
        self.publisher = self.publisher_class(request, **kwargs)
        return super(DetailView, self).dispatch(request, **kwargs)

    def get_object(self, queryset=None):
        return self.publisher.get_object(self.kwargs[self.pk_url_slug])

    def get_queryset(self):
        return self.publisher.get_object_list()

    def get_context_data(self, **kwargs):
        data = super(DetailView, self).get_context_data(**kwargs)
        page = self.publisher.
