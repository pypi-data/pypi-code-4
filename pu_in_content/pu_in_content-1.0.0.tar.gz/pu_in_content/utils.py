from django.conf import settings


def convert_avatar(field):

    img = field.field.to_python(field.value())

    if img:
        return """<img src="%s"/>""" % img.get_avatar_url()
    else:
        return """<img src="%s"/>""" % settings.DEFAULT_AVATAR_URL

def convert_nothing(field):

              return field.value()


CONVERTERS = {'AvatarField': convert_avatar}


def value_to_html(field):

    converter = CONVERTERS.get(field.field.__class__.__name__, convert_nothing)

    return converter(field)
