whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mMenu - define menu
{{/include}}

The <code>whiff_middleware/mMenu</code>
middleware creates a
page
fragment
which implements a
menu implementation based loosely on
<a href="http://www.alistapart.com/articles/dropdowns/">
http://www.alistapart.com/articles/dropdowns/</a>
"""

from whiff.middleware import misc
import menuFromList

MENU_ENTRY = "whiff.middleware.menu.data"
MENU_CLASS_ENTRY = "whiff.middleware.menu.class"

class Menu(misc.utility):
    def __init__(self, page,
                 cssClass=None,
                 height="1em"): 
        self.page = page
        self.height = height
        self.cssClass = cssClass
    def __call__(self, env, start_response):
        # create dictionary for menu information and store it in the env
        menu_list = []
        env = env.copy()
        env[MENU_ENTRY] = menu_list
        # evaluate the page and collect the menu categories
        content = self.param_value(self.page, env)
        height = self.param_value(self.height, env)
        cc = self.cssClass
        if cc is None:
            cc = env.get(MENU_CLASS_ENTRY)
        # format the menu component using external middleware
        menuApp = menuFromList.__middleware__(page=menu_list,
                                              height=height, cssClass=cc)
        menuText = self.param_value(menuApp, env)
        # construct text using text collector list
        L = []
        # add the menu
        L.append(menuText)
        L.append("\n")
        # add content in left aligned div
        L.append('<div style="clear: left;">\n')
        # strip ws from content
        content = content.strip()
        L.append(content)
        L.append('</div>')
        page = "".join(L)
        # deliver constructed text
        return self.deliver_page(page, env, start_response)

__middleware__ = Menu
