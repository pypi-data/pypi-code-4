
whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/menuFromList - format menu from list.
{{/include}}

The <code>whiff_middleware/menuFromList</code>
middleware 
constructs a text for a menu from
list of dictionaries describing categories.
"""

from whiff import gateway
from whiff.rdjson import jsonParse
from whiff.middleware import misc
import types

class menuFromList(misc.utility):
    def __init__(self, page, cssClass=None, height="1em"):
        self.page = page
        self.cssClass = cssClass
        self.height = height
    def __call__(self, env, start_response):
        height = self.param_value(self.height, env)
        menuList = self.param_json(self.page, env)
        focusFunction = gateway.getResource(env, ["freshName", "menuFocusFunction"])
        idList = []
        L = []
        classInfo = ""
        if self.cssClass:
            cssClass = self.param_value(self.cssClass, env)
            classInfo = ' class="%s"' % cssClass
        # top level container list start
        L.append('<ul %s style="padding:0; margin:0; list-style:none;">\n' % classInfo)
        for categoryD in menuList:
            categoryId = gateway.getResource(env, ["freshName", "categoryId"])
            idList.append(categoryId)
            # top category element start
            L.append(' <li')
            categoryclass = categoryD.get('class')
            if categoryclass is not None:
                L.append(' class="%s"' % categoryclass)
            width = categoryD.get('width', '10em') # xxxx magic constant
            L.append(' style="float:left; position:relative; height: %s; width:%s; padding:0; margin:0; list-style:none;"' % (height, width))
            # add mouse events....
            qid = "'%s'" % categoryId
            L.append(' onmouseover="%s(%s)"' % (focusFunction, qid))
            L.append(' onmouseout="%s(%s)"' % (focusFunction, "null"))
            L.append('>\n  ')
            L.append(categoryD["title"])
            L.append("\n")
            # subordinate category list start
            L.append(' <ul style="display:none; position:absolute; top:%s; left:0; padding:0; margin:0; list-style:none;"' % height)
            L.append(' id="%s"' % categoryId)
            L.append('>\n')
            items = categoryD["items"]
            for itemD in items:
                if not type(itemD) is types.DictType:
                    itemD = {"text": itemD}
                # add category member...
                L.append("  <li")
                itemClass = itemD.get("class")
                if itemClass:
                    L.append(' class="%s"' % (itemClass,))
                L.append('>')
                L.append( itemD["text"] )
                L.append('</li>\n')
            # category list end
            L.append(' </ul>\n')
            # category element end
            L.append(' </li>\n')
        # top level container list end
        L.append('</ul>\n')
        # add the javascript focus function definition
        functionDef = FUNCTION_TEMPLATE % (focusFunction, idList)
        L.append(functionDef)
        result = "".join(L)
        return self.deliver_page(result, env, start_response)

FUNCTION_TEMPLATE = """
<script>
function %s(focusId) {
 var idList = %s;
 for (var i=0; i<idList.length; i++) {
     var currentId = idList[i];
     if (currentId!=focusId) {
         var currentelt = document.getElementById(currentId);
         currentelt.style.display="none";
     }
 }
 if (focusId!=null) {
     var focuselt = document.getElementById(focusId);
     focuselt.style.display="block";
 }
}
</script>
"""

__middleware__ = menuFromList
