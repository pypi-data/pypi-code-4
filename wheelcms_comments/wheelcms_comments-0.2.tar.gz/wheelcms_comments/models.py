from django.db import models
from django import forms
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from captcha.fields import CaptchaField

from wheelcms_axle.models import Configuration as BaseConfiguration
from wheelcms_axle.registries.configuration import configuration_registry

from wheelcms_axle.content import type_registry, Content
from wheelcms_axle.templates import template_registry
from wheelcms_axle.spoke import Spoke
from wheelcms_axle.forms import formfactory

class CommentBase(Content):
    class Meta:
        abstract = True

    ## gravatar oid?
    name = models.TextField(blank=False)
    body = models.TextField(blank=False)

class Comment(CommentBase):
    pass

class CommentForm(forms.Form):
    name = forms.Field(label=_('Name'), required=True)
    body = forms.CharField(label=_('Body'), widget=forms.Textarea(attrs={'rows':8, 'cols':40}),
                           required=True)

    if not settings.TESTING:
        ## Do not include this field when running unittests. Make sure you
        ## have test settings with TESTING=True
        captcha = CaptchaField(label=_('Captcha'))


class CommentType(Spoke):
    implicit_add = False   # can't create through frontend directly
    add_to_index = False   # do not index in search
    discussable = False    # well...

    model = Comment
    form = formfactory(Comment)

    title = "A comment"
    # type_icon = icon = ..

template_registry.register(CommentType, "wheelcms_comments/comment_view.html", _("Comment View"), default=True)

type_registry.register(CommentType)

class Configuration(models.Model):
    main = models.ForeignKey(BaseConfiguration, related_name="comments")
    enabled = models.BooleanField(default=True)
    notify_address = models.EmailField(blank=True)

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        exclude = ['main']

configuration_registry.register("comments", "Comments", Configuration, ConfigurationForm)


from wheelcms_axle.actions import action_registry
from django.utils import timezone
import random

def handle_comment_post(handler, request, action):
    
    form = CommentForm(request.POST)
    if not form.is_valid():
        ## since we're redirecting, use sessions to temporarily store
        ## the comment data
        request.session['comment_post'] = request.POST
        return handler.redirect(handler.instance.get_absolute_url(),
                                error=ugettext("Please fix your errors"),
                                hash="commentform")

    name = request.POST.get('name')
    body = request.POST.get('body')
    captcha = request.POST.get('body')

    ## if someone tries really really hard...
    id = "%s-%s" % (timezone.now().strftime("%Y%m%d%H%M%S"),
                    random.randint(0,1000))
    title = _("Comment by %(owner)s on %(date)s") % dict(owner=name, date=timezone.now())

    n = handler.instance.add(id)
    c = Comment(title=title, name=name, body=body, node=n, state="pending").save()

    if 'posted_comments' not in request.session:
        request.session['posted_comments'] = []
    request.session['posted_comments'].append(c.node.path)
    request.session.modified = True
    

    baseconf = BaseConfiguration.config()
    try:
        notify = baseconf.comments.get().notify_address.strip()
    except Configuration.DoesNotExist:
        notify = ""

    sender = baseconf.sendermail.strip()

    if notify and sender:
        content = handler.instance.content()
        domain = Site.objects.get_current().domain
        content_url = "http://%s%s" % (domain, content.get_absolute_url())
        comment_url = "http://%s%s" % (domain, n.get_absolute_url())

        send_mail('New comment on "%s"' % content.title,
                  """A new comment has been posted on "%(title)s" %(content_url)s

Name: %(name)s
Content:
%(body)s

View/edit/delete comment: %(comment_url)sedit""" % dict(title=content.title, content_url=content_url, comment_url=comment_url, name=name, body=body),

                  sender,
                  [notify],
                  fail_silently=True)

    ## log details (ip, etc) in description, or add extra fields
    ## send notification, if enabled
    ## optionally 'recognize' the user and show the comment only to him/her
    ## allow approval/rejection of comment through view?

    return handler.redirect(handler.instance.get_absolute_url(),
                            info="Your comment is being processed")

action_registry.register(handle_comment_post, "post_comment")
