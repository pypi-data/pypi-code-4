from wheelcms_axle.templates import template_registry
from wheelcms_spokes.page import Page, PageType
from wheelcms_axle.content import ImageContent

def frontpage_context(handler, request, node):
    ## limit to images, visible

    language = handler.active_language()
    datanode = node.child('data', language=language)
    if datanode is None:
        return dict(carousel=[])

    images = []
    pages = []

    for n in datanode.children():
        content = n.content()
        if isinstance(content, ImageContent) and content.spoke().workflow().is_visible():
            images.append(n)
        if isinstance(content, Page) and content.spoke().workflow().is_visible():
            pages.append(n)


    return dict(carousel=images, slots=pages)

template_registry.register(PageType, "wheelcms_carousel/page_carousel_view.html",
                           "Carousel view", context=frontpage_context)

