# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives
from django.conf import settings as conf
from django.utils.html import strip_tags
from django.shortcuts import redirect
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime
import models as mymodels
import forms as myforms
import utils

if "rauthall" in conf.INSTALLED_APPS:
    import rauthall.models as rmodels

from django.conf import settings as conf
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView


class ForumListView(ListView):

    template_name = "rforum/forum_list.html"
    context_object_name = "myforum"

    def __init__(self):
        self.sitetitle = conf.SITE_TITLE
        self.sitedescription = conf.SITE_DESCRIPTION

    def get_queryset(self):
        es_moderador = utils.grupo_moderadores(self.request.user)
        if es_moderador:
            return mymodels.Forum.objects.all().filter(status=1, parent__isnull=True)
        else:
            return mymodels.Forum.objects.all().filter(status=1, parent__isnull=True, visible=1)

    def get_context_data(self, **kwargs):
        context = super(ForumListView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Forum index'),
            'description': self.sitedescription,
            'sitetitle': self.sitetitle,
            'sitedescription': self.sitedescription,
        })
        return context


class ForumDetailView(DetailView):

    template_name = "rforum/forum_detail.html"
    context_object_name = "myforum"

    def __init__(self):
        self.sitetitle = conf.SITE_TITLE
        self.sitedescription = conf.SITE_DESCRIPTION

    def get_object(self):
        es_moderador = utils.grupo_moderadores(self.request.user)
        if es_moderador:
            self.obj = get_object_or_404(mymodels.Forum, slug=self.kwargs['slug'], status=1)
        else:
            self.obj = get_object_or_404(mymodels.Forum, slug=self.kwargs['slug'], status=1, visible=1)
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(ForumDetailView, self).get_context_data(**kwargs)

        subforos = ''
        es_moderador = utils.grupo_moderadores(self.request.user)
        if es_moderador:
            subforos = mymodels.Forum.objects.all().filter(status=1, parent=self.obj)
        else:
            subforos = mymodels.Forum.objects.all().filter(status=1, parent=self.obj, visible=1)

        context.update({
            'title': self.obj.title,
            'description': self.obj.title,
            'sitetitle': self.sitetitle,
            'sitedescription': self.sitedescription,
            'subforos': subforos
        })
        return context


class TopicListView(ListView):

    template_name = "rforum/topic_list.html"
    context_object_name = "mypost"

    def __init__(self):
        self.sitetitle = conf.SITE_TITLE
        self.sitedescription = conf.SITE_DESCRIPTION

    def get_queryset(self):
        mytopic = get_object_or_404(mymodels.Topic, slug=self.kwargs['slug2'])
        self.obj = mymodels.Post.objects.all().filter(status=1, topic=mytopic)
        mytopic.hits = mytopic.hits + 1
        mytopic.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['slug2'])
        es_moderador = utils.es_moderador(self.request.user, self.kwargs['slug2'])
        context.update({
            'title': topic.title,
            'description': self.obj[0].body,
            'mytopic': topic,
            'es_moderador': es_moderador,
            'sitetitle': self.sitetitle,
            'sitedescription': self.sitedescription,
        })
        return context



class TopicCreate(FormView):

    """
    Class Based View que agrega un topic con un post asociado.
    """

    form_class = myforms.TopicForm
    template_name = 'rforum/topic_form.html'

    def get_success_url(self):
        forum = get_object_or_404(mymodels.Forum, slug=self.kwargs['slug'])
        return reverse_lazy('app_forum-forum-detail', args=(forum.slug, ))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TopicCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        subject = form.cleaned_data['subject'] # Topic
        message = form.cleaned_data['message'] # Post
        newtopic = mymodels.Topic( user = self.request.user,
                                   forum = get_object_or_404(mymodels.Forum, slug=self.kwargs['slug']),
                                   title = subject,
                                   slug = slugify(subject),
                                   date_created = datetime.now(),
                                   post_count = 1,
                                   topic_count = 1,
                                   hits = 1,
                                   status = 1,
                                   sticky = 0,
                                   closed = 0 )
        newtopic.save()
        newtopic.add_subscriber(self.request.user)
        newtopic.save()
        newpost = mymodels.Post( user = self.request.user,
                                 topic = newtopic,
                                 date_created = datetime.now(),
                                 body = message,
                                 status = 1,)
        newpost.save()
        return super(TopicCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TopicCreate, self).get_context_data(**kwargs)
        forum = get_object_or_404(mymodels.Forum, slug=self.kwargs['slug'])
        if "rauthall" in conf.INSTALLED_APPS:
            userprofile = get_object_or_404(rmodels.UserProfile, user=self.request.user)
        else:
            userprofile = ''
        context.update({
            'myforum': forum,
            'userprofile': userprofile,
        })
        return context


class TopicAction(UpdateView):

    """
    Class Based View que pone un topic como abierto.
    """

    model = mymodels.Topic
    context_object_name = "mypost"

    def get(self, request, *args, **kwargs):
        self.obj = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        if self.kwargs['action']=='open':
            self.obj.closed=0
        if self.kwargs['action']=='close':
            self.obj.closed=1
        if self.kwargs['action']=='sticky':
            self.obj.sticky=1
        if self.kwargs['action']=='unsticky':
            self.obj.sticky=0
        self.obj.save()
        return redirect('app_forum-topic-list', self.obj.forum.slug, self.obj.slug)


    def get_context_data(self, **kwargs):
        context = super(TopicOpenClose, self).get_context_data(**kwargs)
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        context.update({
            'myforum': topic.forum,
        })
        return context


class TopicDelete(DeleteView):

    """
    Class Based View que pone un topic como abierto.
    """

    model = mymodels.Topic
    context_object_name = "mypost"

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        topic.status=0
        topic.save()
        log = mymodels.Log(user=request.user)
        log.action = "%s - [DEL] topic '%s' (status=0)" % (request.user, topic)
        log.save(commit=False)
        #topic.delete()
        return redirect('app_forum-forum-detail', topic.forum.slug)


class PostCreate(CreateView):

    """
    Class Based View que agrega un post nuevo a un topic de un forum (forum -> topic -> post).

    get_success_url(): La url a la que se envía el formulario, también se podría poner de la forma:
                       success_url = 'loquesea', pero necesitaba acceder a self para mantener urls

    dispatch(): Necesario para el decorador login_required
    form_valid(): Se encarga de guardar los valores omitidos en el formulario, ojo porque también
                       se guardan campos en el propio models.py y podría ser que en el propio
                       forms.py también se guardasen (en este caso no es así).
    """

    model = mymodels.Post
    form_class = myforms.PostForm

    def get_success_url(self):
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['slug'], closed=0)
        return reverse_lazy('app_forum-topic-list', args=(topic.forum.slug, self.kwargs['slug'],))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PostCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.date_created = datetime.now()
        form.instance.topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['slug'], closed=0)
        form.instance.topic.add_subscriber(self.request.user)
        """ DEACTIVED: Email subscribers when a new comment is posted """
        for subscriber in form.instance.topic.subscribers.all():
            utils.mysendmail(subscriber.email, 'newpost',
                [form.instance.topic.title,
                form.instance.topic.forum.slug,
                form.instance.topic.slug])
        return super(PostCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PostCreate, self).get_context_data(**kwargs)
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['slug'], closed=0)
        if "rauthall" in conf.INSTALLED_APPS:
            userprofile = get_object_or_404(rmodels.UserProfile, user=self.request.user)
        else:
            userprofile = ''
        context.update({
            'mytopic': topic,
            'userprofile': userprofile,
        })
        return context


class PostUpdate(UpdateView):

    """
    Class Based View que agrega un post nuevo a un topic de un forum (forum -> topic -> post).

    get_success_url(): La url a la que se envía el formulario, también se podría poner de la forma:
                       success_url = 'loquesea', pero necesitaba acceder a self para mantener urls

    dispatch(): Necesario para el decorador login_required
    form_valid(): Se encarga de guardar los valores omitidos en el formulario, ojo porque también
                       se guardan campos en el propio models.py y podría ser que en el propio
                       forms.py también se guardasen (en este caso no es así).
    """

    model = mymodels.Post
    form_class = myforms.PostForm

    def get_success_url(self):
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        return reverse_lazy('app_forum-topic-list', args=(topic.forum.slug, self.kwargs['topicslug'],))

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Post, pk=self.kwargs['id'], status=1)
        return self.obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PostUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 1
        form.instance.topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        return super(PostUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data(**kwargs)
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        if "rauthall" in conf.INSTALLED_APPS:
            userprofile = get_object_or_404(rmodels.UserProfile, user=self.request.user)
        else:
            userprofile = ''
        context.update({
            'mytopic': topic,
            'userprofile': userprofile,
        })
        return context



class PostDelete(DeleteView):

    """
    Class Based View que pone un topic como abierto.
    """

    model = mymodels.Post
    context_object_name = "mypost"

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(mymodels.Topic, slug=self.kwargs['topicslug'])
        self.obj = get_object_or_404(mymodels.Post, id=self.kwargs['id'])
        self.obj.status=0
        self.obj.save()
        #self.obj.delete()
        return redirect('app_forum-topic-list', topic.forum.slug, topic.slug)




def PostReportInnapropiate(request, topicslug, id):

    utils.mysendmail('r0sk10@gmail.com', 'inappropiate', [topicslug, id])
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class UserProfileView(ListView):

    """
    Class Based View que genera la vista de perfil de usuario
    """

    template_name = "rforum/userprofile_view.html"
    context_object_name = "myuser"

    def get_queryset(self):
        return get_object_or_404(User, username=self.kwargs['user'])

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        if "rauthall" in conf.INSTALLED_APPS:
            u = get_object_or_404(User, username=self.kwargs['user'])
            # up = get_object_or_404(rmodels.UserProfile, user=get_object_or_404(User, username=self.kwargs['user']))
            if u.emailaddress_set.filter(verified=True):
                userprofile = get_object_or_404(rmodels.UserProfile, user=get_object_or_404(User, username=self.kwargs['user']))
            else:
                userprofile = get_object_or_404(rmodels.UserProfile, user=get_object_or_404(User, username='nonexistent'))
        else:
            userprofile = ''

        title = u"%s's profile" % userprofile.user.username
        context.update({
            'title': title,
            'userprofile': userprofile,
        })
        return context
