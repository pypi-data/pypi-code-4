
def create_scales_at_adding(image, event):
    """Create scales for edm listing images
       to avoid overlay timeout
       """
    if image.portal_type != 'Image':
        return
    if image.getParentNode().getLayout() != 'edm_folder_listing':
        return

    image.restrictedTraverse('@@images').scale(fieldname='image',
                                               scale='large')
