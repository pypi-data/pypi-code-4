################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implements
from ZPublisher.BaseRequest import DefaultPublishTraverse

class ImageTraverser(DefaultPublishTraverse):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # check __bobo_traverse_ in ATImage
    def publishTraverse(self, request, name):
        """ traverse to image
            image -> field 'image' (original)
            image_scale -> field 'image' (scale)
            image_fieldid -> field fieldid (original)
            image_fieldid_scale -> field fieldid (scale)
            excluding image_view and image_view fullscreen to make standard-views work
        """
        if name.startswith('image') and not name.startswith('image_view'):
            image = None
            namelist = name.split('_')
            l = len(namelist)
            # image
            if l == 1:
                field = self.context.getField(namelist[0])
                image = field.getScale(self.context)
            # image_scale or image_fieldid
            elif l == 2:
                field = self.context.getField(namelist[1])
                # image_scale etc. (old-style)
                if not field:
                    field = self.context.getField(namelist[0])
                    scalename = namelist[1]
                    if scalename in field.getAvailableSizes(self.context).keys():
                        image = field.getScale(self.context,scale=scalename)
                #image_image
                if not image:
                    image = field.getScale(self.context)
            # image_fieldid_scale
            if l == 3: 
                field = self.context.getField(namelist[1])
                scalename = namelist[2]
                if scalename in field.getAvailableSizes(self.context).keys():
                    image = field.getScale(self.context,scale=scalename)
                else:
                    image = field.getScale(self.context)

            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        # default
        return super(ImageTraverser, self).publishTraverse(request, name)
