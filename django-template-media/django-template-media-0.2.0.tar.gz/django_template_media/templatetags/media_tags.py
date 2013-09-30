from contextlib import contextmanager
from django.forms.widgets import Media
from django.template import Library, Node

register = Library()

MEDIA_KEY = '_media'


class MediaContainer(object):
    def __init__(self):
        self.media = Media()
        self.block_media = None
        self.in_media_block = False

    def start_media_block(self):
        """
        Starts ``{% media %}`` block mode.
        """
        self.in_media_block = True
        self.block_media = Media()

    def end_media_block(self):
        """
        Exits ``{% media %}`` block mode, and prepends the accumulated media
        to the page media
        """
        self.in_media_block = False
        self.add_media(self.block_media)
        self.block_media = None

    def add_media(self, media):
        """
        Add the `media` to the current page media. If the page is currently in
        ``{% media %}`` block, the media is appended to the block media,
        otherwise the media is prepended to the site media.
        """
        if media is None:
            return

        if self.in_media_block:
            self.block_media = self.block_media + media
        else:
            self.media = media + self.media

    @contextmanager
    def media_block(self):
        self.start_media_block()
        yield()
        self.end_media_block()

    @classmethod
    def from_context(cls, context):
        if MEDIA_KEY not in context:
            context[MEDIA_KEY] = MediaContainer()

        return context[MEDIA_KEY]


@register.simple_tag(takes_context=True)
def add_media(context, *args):
    medias = filter(lambda m: isinstance(m, Media), args)

    if not bool(medias):
        return ''

    media_container = MediaContainer.from_context(context)
    media_container.add_media(reduce(lambda acc, m: acc + m, medias))

    return ''


@register.simple_tag(takes_context=True)
def add_js(context, *js):
    add_media(context, Media(js=js))
    return ''


@register.simple_tag(takes_context=True)
def add_css(context, media, *css):
    add_media(context, Media(css={media: css}))
    return ''


@register.simple_tag(takes_context=True)
def print_media(context, media_type=None):
    media_container = MediaContainer.from_context(context)
    media = media_container.media

    if media_type is None:
        return media

    return media[media_type]


class MediaNode(Node):
    TAG_NAME = 'media'

    def __init__(self, nodelist):
        super(MediaNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        media_container = MediaContainer.from_context(context)

        with media_container.media_block():
            # Run for its side effects, discard output.
            self.nodelist.render(context)

        return ''


@register.tag(MediaNode.TAG_NAME)
def media(parser, token):
    nodelist = parser.parse(('end' + MediaNode.TAG_NAME,))
    parser.delete_first_token()
    return MediaNode(nodelist)
