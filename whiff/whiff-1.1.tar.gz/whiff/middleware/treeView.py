
whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/treeView - generate a tree view interactive widget
{{/include}}

The <code>whiff_middleware/treeView</code>
middleware generates a tree view widget for interactive
page or data navigation.

"""
# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver
from whiff import gateway
from whiff.rdjson import jsonParse

EXPANDED = "treeView.expandedFlag"
CLOSED = "treeView.closedFlag"
LEAF = "treeView.leafFlag"
TARGETPREFIX = "treeView.targetPrefix"
TARGETSUFFIX = "treeView.targetSuffix"
HEADPREFIX = "treeView.headPrefix"
HEADSEPARATOR = "treeView.headSeparator"
HEADSUFFIX = "treeView.headSuffix"
BODYPREFIX = "treeView.bodyPrefix"
BODYSUFFIX = "treeView.bodySuffix"
TAILPREFIX = "treeView.tailPrefix"
TAILSUFFIX = "treeView.tailSuffix"
TEXTSUFFIX = "treeView.textSuffix"
TEXTPREFIX = "treeView.textPrefix"


DEFAULTS = {
    EXPANDED: "-",
    CLOSED: "+",
    LEAF: "*",
    TEXTSUFFIX: "",
    TEXTPREFIX: "",
    #TEXTPREFIX: """<div style="float:left">""",
    #TEXTSUFFIX: """</div><div style="clear:left"></div>""",
    TARGETPREFIX: '<b><em>',
    TARGETSUFFIX: "</b></em>",
    HEADPREFIX: """<table cellspacing="0"><tr><td valign="top">""",
    HEADSEPARATOR: """</td><td valign="top">""",
    HEADSUFFIX: "</td></tr></table>",
    BODYPREFIX: """
    <table cellspacing="0"><tr><td style="width:20px">&nbsp;</td><td>
    """,
    #BODYPREFIX: """
    #<table cellspacing="0"> <tr> <td style="background-color:black; width:20px">&nbsp;</td><td>
    #""",    
    BODYSUFFIX: """</td></tr></table>""",
    #BODYPREFIX: """<div style="border-left:3px solid black; padding-left:20px">""",
    #BODYSUFFIX: """</div>""",
    #TAILPREFIX:"""
    #<table cellspacing="0"> <tr> <td style="background-color:white; width:20px">&nbsp;</td><td>
    #""",
    TAILPREFIX:"""
    <table cellspacing="0"> <tr> <td style="width:20px">&nbsp;</td><td>
    """,
    TAILSUFFIX:"""</td></tr></table>""",
    #TAILPREFIX: """<div style="padding-left:23px">""",
    #TAILSUFFIX: """</div>""",
    }

def getInfo(env, info, name, defaults=DEFAULTS):
    default = DEFAULTS[name]
    infoval = info.get(name, default)
    result = env.get(name, infoval)
    return result

class treeView(misc.utility):
    def __init__(self,
                 focusNode,
                 infoPath=None,
                 dictionary=None,
                 rootId="",
                 expandIds=None,
                 addNode="",
                 delNode="",
                 callback="reviewTree",
                 withContainer=True,
                 ):
        self.callback = callback
        self.dictionary = dictionary
        self.withContainer = withContainer
        self.infoPath = infoPath
        self.focusNode = focusNode
        self.rootId = rootId
        self.expandIds = expandIds
        self.delNode = delNode
        self.addNode = addNode
        
    def __call__(self, env, start_response):
        callback = self.param_value(self.callback, env).strip()
        withContainer = self.param_json(self.withContainer, env)
        infoPath = self.param_json(self.infoPath, env)
        dictionary = self.param_json(self.dictionary, env)
        focusNode = self.param_value(self.focusNode, env).strip()
        rootId = self.param_value(self.rootId, env).strip()
        expandIds = self.param_json(self.expandIds, env)
        delNode = self.param_value(self.delNode, env).strip()
        addNode = self.param_value(self.addNode, env).strip()
        # manufacture a rootId if not provided
        if not rootId:
            rootId = gateway.getResource(env, ["freshName", "treeViewRootId"])
        #pr "treeView.__call__ (withContainer, infoPath, focusNode, rootId, expandIds, delNode, addNode)=",(withContainer, infoPath, focusNode, rootId, expandIds, delNode, addNode)
        # get the info data structure and wrap it
        infoDict = None
        if dictionary is not None:
            assert infoPath is None, "ambiguous parameters: treeView requires exactly one of info path and dictionary "+repr(infoPath)
            infoDict = dictionary
        else:
            assert infoPath is not None, "no tree data specified.  treeView needs either dictionary or infoPath (but not both)"
            infoDict = gateway.getResource(env, infoPath)
        info = WrapInfo(infoDict)
        # convert the expandIds to a dictionary
        ids = {}
        if expandIds:
            for n in expandIds:
                ids[n] = n
        # add the addNode and children, ancestors, if provided
        if addNode:
            ids[addNode] = addNode
            ids.update( info.children(addNode) )
            ids.update( info.ancestors(addNode) )
            focusNode = addNode
        # remove the delNode (making descendents invisible)
        if delNode:
            if ids.has_key(delNode):
                del ids[delNode]
                delparent = info.parent(delNode)
                if delparent:
                    focusNode = delparent
                #pr "focusNode after delete is", focusNode
            for child in info.children(delNode).keys():
                if ids.has_key(child):
                    del ids[child]
        # use the focusNode to fill in the expandIds with the node, children, ancestors if root is not visible
        rootNode = info.root(focusNode)
        if not ids.has_key(rootNode):
            ids[focusNode] = focusNode
            ids.update( info.children(focusNode) )
            ids.update( info.ancestors(focusNode) )
        # recursively walk the tree to determine node order and levels, determine which are expanded
        (nodesAndLevels, expanded) = info.prefixOrder(rootNode, ids)
        allnodes = expanded.keys()
        allnodes.sort()
        nodesJson = jsonParse.format(allnodes, readable=False)
        L = self.Present(rootNode, ids, info, env, focusNode, callback, nodesJson, rootId)
        prefix = suffix = ""
        if withContainer:
            prefix = '<div id="%s">' % rootId
            suffix = "</div>"
        start_response("200 OK", [('Content-Type', "text/html")])
        return [prefix] + L + [suffix]
    def Present(self, node, ids, info, env, target, callback, nodesJson, rootId, expanded=None):
        if rootId is None:
            rootId = node
        if expanded is None:
            expanded = {}
        assert not expanded.has_key(node), "node presented twice "+repr((node, expanded.keys()))
        # determine expanded children
        allChildrenVisible = True
        visibleChildren = []
        children = info.childrenList(node)
        for child in children:
            if ids.has_key(child):
                visibleChildren.append(child)
            else:
                allChildrenVisible = False
        expanded[node] = allChildrenVisible
        # emit head
        D = {}
        D["text"] = info.body(node)
        D["textprefix"] = getInfo(env, info, TEXTPREFIX)
        D["textsuffix"] = getInfo(env, info, TEXTSUFFIX)
        D["text"] = "%(textprefix)s%(text)s%(textsuffix)s" % D
        ##pr "text is", D["text"]
        #D["text"] = """
        #<div style="overflow:hidden">
        #<div style="float:left">
        #%s
        #</div>
        #<div style="clear:left"></div>
        #</div>""" % info.body(node)
        if children:
            D["rootId"] = jsonParse.format(rootId)
            D["callback"] = callback
            D["target"] = jsonParse.format(target)
            D["nodes"] = nodesJson
            if allChildrenVisible:
                flagchar = getInfo(env, info, EXPANDED) #info.get(EXPANDED, "-")
                addNode = '""'
                delNode = jsonParse.format(node)
            else:
                flagchar = getInfo(env, info, CLOSED) #info.get(CLOSED, "+")
                addNode = jsonParse.format(node)
                delNode = '""'
            D["flagchar"] = flagchar
            D["addNode"] = addNode
            D["delNode"] = delNode
            link = "%(callback)s(%(rootId)s, %(target)s, %(nodes)s, %(addNode)s, %(delNode)s)" % D
            D["link"] = link
            D["flag"] = """<div onclick='%(link)s' style="cursor:crosshair; float:left">
                            %(flagchar)s &nbsp; </div>""" % D
            #D["flag"] = """<a href='javascript:%(link)s' style='text-decoration:none'> %(flagchar)s </a>""" % D
        else:
            D["flag"] = """<div style="float:left">%s &nbsp;</div>""" % getInfo(env, info, LEAF) #info.get(LEAF, "*")
        D["prefix"] = D["suffix"] = ""
        if node==target:
            D["prefix"] = getInfo(env, info, TARGETPREFIX) #info.get(TARGETPREFIX, "<b><em>")
            D["suffix"] = getInfo(env, info, TARGETSUFFIX) #info.get(TARGETSUFFIX, "</b></em>")
        #D["flag"] = "%(prefix)s %(flag)s %(suffix)s" % D
        D["hprefix"] = getInfo(env, info, HEADPREFIX) # <br>
        D["hseparator"] = getInfo(env, info, HEADSEPARATOR)
        D["hsuffix"] = getInfo(env, info, HEADSUFFIX)
        head = """
        %(hprefix)s
        %(flag)s %(hseparator)s %(prefix)s%(text)s%(suffix)s
        %(hsuffix)s
        """ % D
        # emit body, including all children, except last, and head of last child
        bodyL = []
        cbody = ctail = suffix = ""
        if visibleChildren:
            bodyL.append(getInfo(env, info, BODYPREFIX)) #("""<div style="border-left:3px solid black; padding-left:20px">""")
            lastChild = visibleChildren[-1]
            for child in visibleChildren[:-1]:
                bodyL.extend(self.Present(child, ids, info, env, target, callback, nodesJson, rootId, expanded))
            [chead, cbody, ctail] = self.Present(lastChild, ids, info, env, target, callback, nodesJson, rootId, expanded)
            bodyL.append(chead)
            bodyL.append(getInfo(env, info, BODYSUFFIX)) #("""</div>""")
        body = "\n".join(bodyL)
        # emit tail, including body, tail of last child
        tail = ""
        if cbody or ctail:
            Ltail = []
            Ltail.append(getInfo(env, info, TAILPREFIX)) #("""<div style="padding-left:23px">""")
            Ltail.append(cbody)
            Ltail.append(ctail)
            Ltail.append(getInfo(env, info, TAILSUFFIX)) #("""</div>""")
            tail = "\n".join(Ltail)
        return [head, body, tail]

class WrapInfo:
    def __init__(self, infoDict):
        self.infoDict = infoDict
    def get(self, key, default):
        try:
            return self.infoDict[key]
        except KeyError:
            return default
    def parent(self, NodeName):
        return self.infoDict[NodeName].get("parent", None)
    def body(self, NodeName):
        return self.infoDict[NodeName]["body"]
    def childrenList(self, NodeName):
        return self.infoDict[NodeName].get("children", [])
    def children(self, NodeName):
        clist = self.infoDict[NodeName].get("children", [])
        cdict = {}
        for child in clist:
            cdict[child] = child
        return cdict
    def ancestors(self, NodeName, root_only=False):
        adict = {}
        adict[NodeName] = NodeName
        root = NodeName
        p = self.parent(NodeName)
        while p is not None:
            if adict.has_key(p):
                raise ValueError, "looping computing ancestors: "+repr((NodeName, p))
            adict[p] = p
            root = p
            p = self.parent(p)
        if root_only:
            return root
        else:
            return adict
    def root(self, NodeName):
        return self.ancestors(NodeName, root_only=True)
    def prefixOrder(self, fromNodeName, nodeDict, level=0, nodesAndLevels=None, expanded=None):
        if nodesAndLevels is None:
            nodesAndLevels = []
        if expanded is None:
            expanded = {}
        if nodeDict.has_key(fromNodeName):
            if expanded.has_key(fromNodeName):
                raise ValueError, "saw node twice "+repr(fromNodeName)
            has_all_children = True
            ChildNodesAndLevels = []
            for child in self.childrenList(fromNodeName):
                if nodeDict.has_key(child):
                    (ChildNodesAndLevels, expanded) = self.prefixOrder(child, nodeDict, level+1, ChildNodesAndLevels, expanded)
                else:
                    has_all_children = False
            expanded[fromNodeName] = has_all_children
            nodesAndLevels.append( (fromNodeName, level) )
            nodesAndLevels.extend( ChildNodesAndLevels )
        return (nodesAndLevels, expanded)

__middleware__ = treeView
