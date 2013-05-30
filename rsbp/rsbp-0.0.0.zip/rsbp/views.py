from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from .models import Post, Tag
from . import app_settings


class PostListView(ListView):

    template_name = 'rsbp/post_list.html'
    paginate_by = app_settings.RSBP_POSTS_PER_PAGE

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Post.objects.all()
        else:
            return Post.objects.filter(published=True)


class TagView(PostListView):

    template_name = 'rsbp/tag_list.html'

    def get_queryset(self):
        qs = super(TagView, self).get_queryset()

        self.do_and = self.request.GET.has_key('and') or self.request.GET.has_key('AND')

        tags = self.kwargs.get('tags', '').split('/')
        self.tags = []

        for tag in tags:
            if tag:
                try:
                    self.tags.append(Tag.objects.get(text=tag))
                except Tag.DoesNotExist:
                    if self.do_and:
                        self.tags = []
                        break
                    continue

        if self.do_and:
            if not self.tags:
                qs = qs.none()
            else:
                for tag in self.tags:
                    qs = qs.filter(tags__id=tag.id)
        else:
            qs = qs.filter(tags__in=[t.id for t in self.tags]).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['tags_display'] = ', '.join([t.text for t in self.tags])
        return context


class PostView(DetailView):

    template_name = 'rsbp/post.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        title_slug = self.kwargs.get('title_slug', u'') or u''
        if title_slug != self.object.slug:
            return HttpResponseRedirect(reverse('post', args=(self.object.id, self.object.slug)))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return obj
