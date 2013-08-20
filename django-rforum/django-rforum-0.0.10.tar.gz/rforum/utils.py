# -*- coding: utf-8 -*-
import models as mymodels
from django.contrib.auth.models import User
from django.conf import settings as conf
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.models import Site


def es_suyo(usuario, id):

    """
    Devuelve True si el usuario es propietario del topic que le pasamos como
    parámetro o False si no lo es.
    """

    #User.objects.get(username=usuario)
    if usuario.is_superuser:
        return True

    mytopic = mymodels.Post.objects.get(id=id)

    #print "*"*80
    #print id
    #print usuario
    #print mytopic.user
    #print "*"*80
    #import pdb; pdb.set_trace()

    if(mytopic.user == usuario):
        return True
    else:
        return False


def es_moderador(usuario, topicslug):

    """
    Devuelve True si el usuario es moderador del foro al que corresponde el
    topic que le pasamos como parámetro o False si no lo es.
    """

    #print "--------------"
    #print usuario
    #print topicslug
    #import pdb; pdb.set_trace()

    #User.objects.get(username=usuario)
    if usuario.is_superuser:
        return True

    mytopic = mymodels.Topic.objects.get(slug=topicslug)
    moderators = mytopic.forum.moderators
    #print moderators.all()
    try:
        moderators.get(username=usuario)
        return True
    except User.DoesNotExist:
        return False


def grupo_moderadores(usuario):

    """
    Devuelve True si el usuario pertenece al grupo de moderadores
    o False si no lo es.
    """

    #import pdb; pdb.set_trace()
    #User.objects.get(username=usuario)
    #import pdb; pdb.set_trace()
    qs = User.objects.filter(groups__name=conf.MODERATORS_GROUP_NAME, username=usuario.username)

    if qs:
        #print "si"
        return True
    else:
        #print "no"
        return False


def mysendmail(email, mytype, arguments):

    current_site = Site.objects.get_current()

    # favour django-mailer but fall back to django.core.mail
    if "mailer" in conf.INSTALLED_APPS:
        from mailer import send_mail
        from mailer import send_html_mail
    else:
        from django.core.mail import send_mail
        from django.core.mail import send_mail as send_html_mail

    if mytype == 'newpost':
        subject =  _('[%s] New post in "%s"') % (conf.SITE_TITLE, arguments[0])
        from_email = conf.DEFAULT_FROM_EMAIL
        to = email
        html_content = render_to_string('rforum/email_subscribers_newpost.html',
                                        {'title': arguments[0],
                                        'slug': arguments[1],
                                        'topicslug': arguments[2],
                                        'domain': current_site.domain })
        text_content = strip_tags(html_content)

    if mytype == 'inappropiate':
        subject =  _('[%s] Post marked as inappropiate') % (conf.SITE_TITLE)
        from_email = conf.DEFAULT_FROM_EMAIL
        to = email
        html_content = render_to_string('rforum/email_inappropiate.html',
                                        {'slug': arguments[0],
                                        'domain': current_site.domain })
        text_content = strip_tags(html_content)

    send_html_mail(subject, text_content, html_content, from_email, [to])


