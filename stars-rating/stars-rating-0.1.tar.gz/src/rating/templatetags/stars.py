### -*- coding: utf-8 -*- ####################################################
import random
import string

from django import template
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

register = template.Library()

BIG_STAR_WIDTH = getattr(settings, 'BIG_STAR_WIDTH', 28)
HASH_LENGTH = 5

@register.inclusion_tag('stars.html', takes_context=True)
def show_stars(context, obj, field_name='rating', big_star=True, disabled=False, extra_class='', extra_success=''):
    request = context['request']
    rating = getattr(obj, field_name)
    content_type = ContentType.objects.get_for_model(obj)
    hash = ''.join(random.choice(string.ascii_letters) for n in range(0, HASH_LENGTH))
    return {
        'scores': range(rating.field.range + 1),
        'rating': int(rating.get_rating_for_user(request.user, request.META['REMOTE_ADDR'], request.COOKIES) or rating.get_rating()),
        'object': obj,
        'field_name': field_name,
        'content_type_id': content_type.pk,
        'user': request.user,
        'disabled': disabled or not (rating.field.allow_anonymous or request.user.is_authenticated()),
        'starWidth': big_star and BIG_STAR_WIDTH or 0,
        'stars_id': "%s_%s_%s_%s_%s" % (content_type.app_label, content_type.model, obj.pk, field_name, hash),
        'extra_class': extra_class,
        'extra_success': extra_success,
    }
