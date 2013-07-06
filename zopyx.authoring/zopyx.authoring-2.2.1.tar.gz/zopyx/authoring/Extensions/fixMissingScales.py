

SIZES = {'mini': (200, 200), 
         'thumb': (128, 128), 
         'large': (768, 768), 
         'listing': (16, 16), 
         'tile': (64, 64), 
         'preview': (400, 400), 
         'icon': (32, 32)}

def fixMissingScales(self):

    for brain in self.portal_catalog(portal_type='Image'):
        img = brain.getObject()
        img_field = img.getField('image')
        sizes =  img_field.getAvailableSizes(img)
        print img.absolute_url(1), sizes
        if not sizes:
            img_field.sizes = SIZES
            img_field.createScales(img)

    return 'done'


