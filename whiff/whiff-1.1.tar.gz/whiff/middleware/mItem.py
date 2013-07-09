whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mItem - define menu item
{{/include}}

The <code>whiff_middleware/mItem</code>
middleware defines a 
menu item for inclusion in a drop
down menu.
"""

from whiff.middleware import misc
import mCategory

ITEM_CLASS_ENTRY = "whiff.middleware.mItem.class"

class Item(misc.utility):
    def __init__(self,
                 page,
                 cssClass=None):
        self.page = page
        self.cssClass = cssClass
    def __call__(self, env, start_response):
        # find the category descriptor
        categoryDescriptor = env.get(mCategory.CATEGORY_ENTRY)
        assert categoryDescriptor is not None, "menu item only makes sense inside a menu category"
        # construct item descriptor
        page = self.param_value(self.page, env)
        itemDict = {}
        itemDict["text"] = page
        cc = self.cssClass
        if cc is None:
            cc = env.get(ITEM_CLASS_ENTRY)
        if cc:
            itemDict["class"] = self.param_value(cc, env)
        # append descriptor to category items
        categoryDescriptor.append(itemDict)
        # return empty string as content (real return is to category descriptor)
        return self.deliver_page("", env, start_response)

__middleware__ = Item
