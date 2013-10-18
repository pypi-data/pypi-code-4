from stroller.lib import stroller_url
from stroller.lib import IconLink

__all__ = ['stroller_url', 'icons', 'category_icon']

icons = {
    'checkout':IconLink(modname='stroller', filename='static/checkout.png', alt='Checkout!'),
    'big-cart':IconLink(modname='stroller', filename='static/cart.png', alt='Add to Cart'),
    'delete':IconLink(modname='stroller', filename='static/delete.png', alt='Delete Product'),
    'featured_add':IconLink(modname='stroller', filename='static/featured.png', alt='Make Featured'),
    'featured_del':IconLink(modname='stroller', filename='static/featured_rm.png', alt='Remove Featured'),
    'folder':IconLink(modname='stroller', filename='static/folder.png', alt='Category'),
    'clone':IconLink(modname='stroller', filename='static/clone.png', alt='Clone Product'),
    'edit':IconLink(modname='stroller', filename='static/edit.png', alt='Edit Product'),
    'list':IconLink(modname='stroller', filename='static/list.png', alt='List Orders'),
    'cancel':IconLink(modname='stroller', filename='static/cancel.png', alt='Cancel')
}

def category_icon(category):
    if category.icon:
        return '<img src="%s"/>' % stroller_url('/category_icon', uid=category.uid)
    else:
        return icons['folder']
