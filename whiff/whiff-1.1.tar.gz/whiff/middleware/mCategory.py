
whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mCategory - define menu category
{{/include}}

The <code>whiff_middleware/mCategory</code>
middleware encloses a
menu category with title and items.
"""

from whiff.middleware import misc
import mMenu

CATEGORY_ENTRY = "whiff.middleware.menu.category"
CATEGORY_CLASS_ENTRY = "whiff.middleware.mCategory.class"

class Category(misc.utility):
    def __init__(self,
                 title,
                 items,
                 cssClass=None):
        self.title = title
        self.items = items
        self.cssClass = cssClass
    def __call__(self, env, start_response):
        # find the menu descriptor list
        menuDescriptor = env.get(mMenu.MENU_ENTRY)
        assert menuDescriptor is not None, "menu category only makes sense inside a menu"
        item_list = []
        env = env.copy()
        env[CATEGORY_ENTRY] = item_list
        # evaluate the items, collecting item information
        content = self.param_value(self.items, env)
        # append a category descriptor to the menu descriptor
        descriptor = {}
        descriptor["title"] = self.param_value(self.title, env)
        descriptor["items"] = item_list
        cc = self.cssClass
        if cc is None:
            cc = env.get(CATEGORY_CLASS_ENTRY)
        if cc:
            descriptor["class"] = self.param_value(cc, env)
        menuDescriptor.append(descriptor)
        return self.deliver_page(content, env, start_response)

__middleware__ = Category
