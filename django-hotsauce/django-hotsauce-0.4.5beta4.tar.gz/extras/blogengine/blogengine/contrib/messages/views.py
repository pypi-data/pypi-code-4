
from datetime   import datetime
from base64     import urlsafe_b64decode
#from operator  import attrgetter

from notmm.utils.decorators import with_schevo_database
from notmm.utils.wsgilib    import HTTPRedirectResponse as HTTPRedirect
from notmm.dbapi.orm        import schevo_compat

### blogengine imports
from blogengine.messages.forms import MessageForm
from blogengine.model import MessageManager, AuthorDoesNotExist
from blogengine.shortcuts import direct_to_template
from blogengine.utils import post_required

### libauthkit imports
from authkit.authorize.django_adaptors2 import authorize
from authkit.permissions import RemoteUser

auth_db = schevo_compat.XdserverProxy('accounts')
blog_db = schevo_compat.XdserverProxy('blogengine')

#@authorize(UserIn(['editors'])
@authorize(RemoteUser())
@with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def message_list(request, **kwargs):
    """return a list of posted messages by the current user """

    db = request.environ[settings.DATABASE_NAME]
    ctx = dict()

    # this should be redefined inside MessageManager
    username = request.user #XXX should be a Python class instance :)
    author = db.Author.findone(username=username)
    try:
        message_set = db.Q.Match(db.Message, 'author', '==', author)
        ctx['message_set'] = list(message_set())
    except (ValueError,TypeError):
        ctx['message_set'] = []

    return direct_to_template(request, \
        template_name='blogengine/messages/message_list.mako',
        extra_context=ctx
        )

@authorize(RemoteUser())
def post(request, **kwargs):
    """ save a new message in the db """

    new_data = request.POST.copy()

    form = MessageForm(data=new_data)
    if form.is_valid():
        # create the transaction instance
        create_tx = blog_db.Message.t.create()
        create_tx.content = new_data['content']
        # verify the authorized user is a valid Author
        author = auth_db.Author.findone(username=request.user)
        print author
        #if author is None:
        #    author = "guest"
        create_tx.author = author
        # manually add pub_date
        create_tx.pub_date = datetime.now()
        #print "author: %r" % author

        blog_db.execute(create_tx)
        blog_db.commit()

    #XXX need to return to the user "message board" page
    #XXX use request.user.is_authenticated()
    if request.user is not None:
        redirect_to = "/users/%s/messages/" % str(request.user)
    else:
        redirect_to = "/users/guest/messages/" # "sandbox" like page for visitors...
    return HTTPRedirect(location=redirect_to)
post = post_required(post)

@with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def details(request, **kwargs):

    db = request.environ[settings.SCHEVO['DATABASE_NAME']]
    db._sync()
    ctx = {}

    if 'oid' in kwargs:
        #XXX this is simply a base64 encoded string
        b64data = urlsafe_b64decode(kwargs['oid'])
        key, oid = b64data.split(':')
        assert key==settings.SECRET_ID
        obj = MessageManager.objects.get_by_oid(oid)
        ctx['content'] = obj.content
        ctx['pub_date'] = obj.pub_date.strftime("%Y-%m-%d %Z")
        ctx['username'] = obj.author.username
        #ctx['tellafriend'] 

    return direct_to_template(request, \
        template_name='blogengine/messages/message_details.mako',
        extra_context=ctx)
