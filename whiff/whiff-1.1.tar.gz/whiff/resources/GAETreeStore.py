"""
Store Wiki Dictionary in Google App Engine.
"""

from google.appengine.ext import db
import time
import myhash
from whiff.middleware import misc

class NodeKeyError(KeyError):
    "can't find node"

FORBIDDENID = "tree"

def inventNodeIdentity(parentId, rootId):
    L = []
    root = getNode(rootId, rootId)
    parent = getNode(rootId, parentId)
    while 1:
        L.append(time.time())
        L.append(root.modTime)
        L.append(parent.title)
        L.append(parent.body)
        s = repr(L)
        identity = myhash.asciiHash(s)
        if identity!=FORBIDDENID and getNode(rootId, identity) is None:
            return identity
        L = [identity]
        # repeat until unique value found

class Root(db.Model):
    """
    storage for tree root special annotations
    """
    identity = db.StringProperty()
    createTime = db.DateTimeProperty(auto_now_add=True)
    editPassword = db.StringProperty()

class Node(db.Model):
    """
    storage for tree node information
    """
    identity = db.StringProperty()
    parentId = db.StringProperty()
    rootId = db.StringProperty()
    creatorNick = db.StringProperty()
    title = db.StringProperty()
    body = db.TextProperty()
    ordering = db.IntegerProperty()
    isComment = db.BooleanProperty()
    editSource = db.BooleanProperty()
    modTime = db.DateTimeProperty(auto_now_add=True)

def rootNameOk(name):
    if len(name)>30:
        return False
    try:
        name = unicode(name)
    except:
        return False
    else:
        return name.isalnum()

def newRoot(identity, password, creatorNick):
    "return  a new root with identity or return None if taken"
    if getRoot(identity) is not None or identity==FORBIDDENID or not rootNameOk(identity):
        return None # taken identity
    result = Root()
    result.identity = identity
    result.editPassword = password
    result.put()
    # also create a Node for the root under the root
    newNode(identity, identity, identity, creatorNick,
            title="temporary title for "+identity,
            body="temporary description for "+identity,
            isComment=False,
            editSource=False,
            check=False,
            )
    return result
            
def newNode(identity, parentId, rootId, creatorNick,
            title, body, isComment, editSource, check=True):
    if identity is None:
        identity = inventNodeIdentity(parentId, rootId)
    assert getNode(rootId, identity) is None, "cannot create node, exists "+repr((
        rootId, identity))        
    node = Node()
    setNode(node, identity, parentId, rootId, creatorNick,
            title, body, isComment, editSource, check)
    return node

def setNode(node, identity=None, parentId=None, rootId=None, creatorNick=None,
            title=None, body=None, isComment=None, editSource=None, check=True):
    if check:
        if rootId is not None:
            assert getRoot(rootId) is not None, "no such root "+repr(rootId)
            if parentId is not None and rootId!=parentId:
                assert getNode(rootId, parentId) is not None, "no such parent "+repr((
                    parentId, rootId))
    if identity is not None:
        node.identity = identity
    if parentId is not None:
        node.parentId = parentId
    if rootId is not None:
        node.rootId = rootId
    if creatorNick is not None:
        node.creatorNick = creatorNick[:200]
    if title:
        node.title = title[:200]
    if body:
        node.body = unicode(body, "utf8", "ignore")
    if isComment is not None:
        node.isComment = isComment
    if editSource is not None:
        node.editSource = editSource
    node.put()

def getNode(rootIdentity, identity):
    test = list(db.GqlQuery("SELECT * FROM Node WHERE identity=:1 AND rootId=:2",
                            identity, rootIdentity)
                )
    if test:
        #pr "GOT NODE WITH BODY"
        #pr repr(test[0].body)
        return test[0]
    return None

def getChildrenNodes(rootIdentity, identity):
    # order by doesn't work here (totally bizarre...)
    #test = list(db.GqlQuery("SELECT * FROM Node WHERE parentId=:1 AND rootId=:2 and identity!=:1 ORDER BY modTime",...)
    test = list(db.GqlQuery("SELECT * FROM Node WHERE parentId=:1 AND rootId=:2 and identity!=:1",
                            identity, rootIdentity)
                )
    if test:
        orderer = [(x.modTime, x) for x in test]
        orderer.sort()
        test = [y for (x,y) in orderer]
    return test

def delNode(rootIdentity, identity):
    node = getNode(rootIdentity, identity)
    assert node is not None, "no such node to delete "+repr(identity)
    parent = node.parentId
    assert parent and not (parent==identity), "cannot delete root node for tree"
    children = getChildrenNodes(rootIdentity, identity)
    assert not children, "cannot delete node with descendents "+repr(identity)
    node.delete()
    return parent

def getRoot(identity):
    test = list(db.GqlQuery("SELECT * FROM Root WHERE identity=:1", identity))
    if test:
        return test[0]
    return None

class GAETreeMapping:
    "dict like structure for getting tree info"
    append = True
    def __init__(self, rootId, bodyTemplate, env):
        self.env = env
        self.rootId = rootId
        self.bodyTemplate = bodyTemplate
        self.cache = {}
    def __repr__(self):
        return "GAETreeMapping" + repr((self.rootId,))
    def __getitem__(self, nodeId):
        result = self.cache.get(nodeId)
        if result is None:
            result = self.getitem(nodeId)
        self.cache[nodeId] = result
        return result
    def getitem(self, nodeId):
        rootId = self.rootId
        thenode = getNode(rootId, nodeId)
        if thenode is None:
            raise NodeKeyError, "cannot find any node for "+repr((rootId, nodeId))
        children = getChildrenNodes(rootId, nodeId)
        D = {}
        if thenode.parentId and thenode.parentId!=nodeId:
            D["parent"] = thenode.parentId
        if children:
            D["children"] = [ c.identity for c in children ]
        D["body"] = self.body(thenode, children)
        return D
    def body(self, node, children):
        D = self.env.copy()
        D["body"] = node.body
        D["title"] = node.title
        D["creatorNick"] = node.creatorNick
        D["node"] = node.identity
        D["rootId"] = self.rootId
        D["className"] = repr(self)
        D["append"] = self.append
        D["children"] = 0
        D["parent"] = node.parentId
        D["editSource"] = node.editSource
        if children:
            D["children"] = len(children)
        return self.format(self.bodyTemplate, D)
    def format(self, template, env):
        iterator = template(env, misc.ignore)
        L = list(iterator)
        return "".join(L)
##    def body0(self, node):
##        D = {}
##        D["body"] = node.body
##        D["title"] = node.title
##        D["creatorNick"] = node.creatorNick
##        D["node"] = node.identity
##        D["parent"] = node.parent
##        D["rootId"] = self.rootId
##        D["className"] = repr(self)
##        return BODYTEMPLATE % D

##BODYTEMPLATE = """
##<div style="float:left;">
##<b>
##<a href="/%(rootId)s/%(node)s/">%(title)s</a>
##</b>
##&nbsp; <a href="/%(rootId)s/%(node)s/edit">[edit]</a>
##<br>
##<table>
##<tr> <td>%(body)s</td> </tr>
##<tr> <td align="right"><em>%(creatorNick)s</em></td> </tr>
##<tr> <a href="/%(rootId)s/%(node)s/append">append entry</a>
##</table>
##</div>
##<div style="clear:left;"></div>
##<!--
##node: %(node)s of root %(rootId)s presented by %(className)s
##-->
##"""

class GAETreeUpdateMapping(GAETreeMapping):
    append = False
    def __init__(self, rootId, updateNode, actionUrl, bodyTemplate, updateTemplate, env):
        GAETreeMapping.__init__(self, rootId, bodyTemplate, env)
        self.env = env
        self.updateNode = updateNode
        self.actionUrl = actionUrl
        self.updateTemplate = updateTemplate
    def __repr__(self):
        return "GAETreeUpdateMapping"+ repr((self.rootId, self.updateNode, self.actionUrl))
    def body(self, node, children):
        from whiff import whiffenv
        if node.identity!=self.updateNode:
            return GAETreeMapping.body(self, node, children)
        D = self.env.copy()
        D["rootId"] = self.rootId
        D["updateNode"] = self.updateNode
        D["actionUrl"] = self.actionUrl
        D["title"] = whiffenv.cgiGet(D, "title", node.title)
        D["body"] = whiffenv.cgiGet(D, "body", node.body)
        D["password"] = whiffenv.cgiGet(D, "password", "")
        D["children"] = len(children)
        getUserAndPass(D)
        D["creatorNick"] = node.creatorNick
        D["editSource"] = testEditSource(D, node)
        #pr "update edit source", D["editSource"]
        return self.format(self.updateTemplate, D)

def testEditSource(env, node=None):
    from whiff import whiffenv
    cgiEditSourcestr = whiffenv.cgiGet(env, "editSource", None)
    #pr "cgiEditSourcestr", cgiEditSourcestr
    cgiEditSource = (cgiEditSourcestr=="true")
    if cgiEditSourcestr is not None:
        return cgiEditSource
    elif node:
        return node.editSource
    else:
        return False
##UPDATETEMPLATE = """
##<em>Update entry:</em>
##<hr>
##<form action="%(actionUrl)s" method="POST">
##<input type="hidden" name="rootId" value="%(rootId)s">
##<input type="hidden" name="updateNode" value="%(updateNode)s">
##<b>title: <input name="title" value="%(title)s"> </b><br>
##<table>
##<tr> <td>
##body<br>
##   <textarea cols="50" rows="3" name="body">%(body)s</textarea>
##</td> </tr>
##<tr> <td align="right"><em>%(creatorNick)s</em></td> </tr>
##<tr> <td>
##     <input type="submit" name="save" value="save">
##     <a href="/%(rootId)s/%(updateNode)s">cancel</a>
##</td></tr>
##</table>
##</form>
##</hr>
##"""

class GAETreeCreateMapping(GAETreeMapping):
    append = False
    def __init__(self, rootId, parentId, actionUrl, bodyTemplate, createTemplate, env ):
        GAETreeMapping.__init__(self, rootId, bodyTemplate, env)
        self.env = env
        self.createTemplate = createTemplate
        self.parentId = parentId
        self.actionUrl = actionUrl
    def __repr__(self):
        return "GAETreeUpdateMapping"+ repr((self.rootId, self.parentId, self.actionUrl))
    def getitem(self, identity):
        if identity==FORBIDDENID:
            D = {}
            D["parent"] = self.parentId
            D["body"] = self.addBody()
            return D
        D = GAETreeMapping.getitem(self, identity)
        if identity==self.parentId:
            children = D.get("children", [])
            children.append(FORBIDDENID)
            D["children"] = children
        return D
    def addBody(self):
        from whiff import whiffenv
        D = self.env.copy()
        D["actionUrl"] = self.actionUrl
        D["rootId"] = self.rootId
        D["parentId"] = self.parentId
        # NEED TO GET BODY, TITLE FROM CGI PARAMETERS!
        D["body"] = whiffenv.cgiGet(D, "body", "")
        D["title"] = whiffenv.cgiGet(D, "title", "")
        D["password"] = whiffenv.cgiGet(D, "password")
        D["creatorNick"] = whiffenv.cgiGet(D, "creatorNick")
        D["editSource"] = testEditSource(D, node=None)
        #pr "create edit source", D["editSource"]
        getUserAndPass(D)
        return self.format(self.createTemplate, D)

ADDTEMPLATE = """
<em>New entry</em>
<hr>
<form action="%(actionUrl)s" method="POST">
<input type="hidden" name="rootId" value="%(rootId)s">
<input type="hidden" name="parentId" value="%(parentId)s">
<b>  title: <input name="title" value="%(title)s"> </b><br>
<table>
<tr> <td>
body:<br>
   <textarea cols="50" rows="3" name="body">%(body)s</textarea>
</td> </tr>
<tr> <td align="right"><em>your name: <input name="creatorNick" value=""></em></td> </tr>
<tr> <td>
     <input type="submit" name="save" value="save">
     <a href="/%(rootId)s/%(parentId)s">cancel</a>
     </td></tr>
</table>
</form>
"""

class TreeResource:
    def __init__(self, bodyTemplate, updateTemplate, createTemplate, env=None):
        self.bodyTemplate = bodyTemplate
        self.updateTemplate = updateTemplate
        self.createTemplate = createTemplate
        self.env = env
    def localize(self, env):
        bt = self.bodyTemplate
        ut = self.updateTemplate
        ct = self.createTemplate
        return TreeResource(bt, ut, ct, env)
    def get(self, pathlist):
        assert len(pathlist)>1, "pathlist must include the mode and the rootId"+repr(pathlist)
        mode = pathlist[0]
        rootId = pathlist[1]
        if mode=="view":
            return GAETreeMapping(rootId, self.bodyTemplate, self.env)
        else:
            assert len(pathlist)==4, "non-view must include mode, rootid, focusid, url only: "+repr(pathlist)
            nodeId = pathlist[2]
            url = pathlist[3]
            if mode=="update":
                return GAETreeUpdateMapping(rootId, nodeId, url, self.bodyTemplate, self.updateTemplate, self.env)
            elif mode=="append":
                return GAETreeCreateMapping(rootId, nodeId, url, self.bodyTemplate, self.createTemplate, self.env)
            else:
                raise ValueError, "I don't understand this resource path "+repr(pathlist)
        raise ValueError, "unreachable code"

def getUserAndPass(env, envcreator=None, envpassword=None, passwordOk=True):
    """
    look for "creatorNick" and "password" in the environment
    look for resources ["session", "item", "creatorNick"] ["session", "item", "password"]
    if the differ resolve them prefering environment values
    """
    from whiff import gateway
    if not envcreator:
        envcreator = env.get("creatorNick")
    if not envpassword:
        envpassword = env.get("password")
    creatorPath = ["session", "item", "creatorNick"]
    passwordPath = ["session", "item", "password"]
    sesscreator = gateway.getResource(env, creatorPath, "")
    sesspassword = gateway.getResource(env, passwordPath, "")
    #pr "got session password", (sesspassword, envpassword, passwordOk)
    if envcreator and envcreator!=sesscreator:
        gateway.putResource(env, creatorPath, envcreator)
        env["creatorNick"] = envcreator
    else:
        env["creatorNick"] = sesscreator
    if passwordOk:
        if envpassword and envpassword!=sesspassword:
            gateway.putResource(env, passwordPath, envpassword)
            env["password"] = envpassword
        else:
            env["password"] = sesspassword
    else:
        #pr "putting blank password", (passwordPath, "")
        gateway.putResource(env, passwordPath, "")
        env["password"] = ""

def passwordOk(env, rootId, password):
    from whiff import gateway
    from whiff import whiffenv
    result = False
    theRoot = getRoot(rootId)
    if theRoot is None:
        #pr "passswordOk: NO ROOT!"
        result = True # ???
    else:
        thePassword = theRoot.editPassword
        if password:
            password = password.strip()
        if thePassword:
            thePassword = thePassword.strip()
        #pr "passworkOk testing", (password, thePassword)
        if thePassword:
            test =  (password==thePassword)
            #pr "passwordOk test", test
            result = test
        else:
            # no password, anything goes
            #pr "no password to Ok"
            result = True
    if not result:
        passwordPath = ["session", "item", "password"]
        gateway.putResource(env, passwordPath, "")
        whiffenv.cgiPut(env, "password", "")
        env["password"] = ""
    return result
