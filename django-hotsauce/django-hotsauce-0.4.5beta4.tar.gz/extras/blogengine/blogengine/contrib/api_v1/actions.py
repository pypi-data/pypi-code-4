# Copyright (c) 2009-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Management views"""

import os

# support functions
from datetime import datetime

from notmm.dbapi.orm import decorators
from notmm.utils.django_settings import LazySettings
from notmm.utils.wsgilib import HTTPUnauthorized
from blogengine.template import direct_to_template
from blogengine.contrib.comments import CommentForm
from blogengine.config import RemoteUser, authorize
from .forms import EntryForm
from .model import CategoryManager, EntryManager

settings = LazySettings()

@authorize(RemoteUser(), HTTPUnauthorized)
def send_to_friend(request, slug, template_name="blogengine/api/tell_a_friend.mako"):
    from blogengine.forms import SendToFriendForm

    obj = EntryManager.objects.get_by_slug(oid)
    
    form = SendToFriendForm(initial={
        'subject': obj.title,
        'message': 'You can add a personal message here to your recipients.'})

    ctx = {
        'title': 'Send to friend',
        'slug'  : str(oid),
        'obj'  : obj,
        'message': 'You can use the form below to share this article with friends.'}
    
    ctx['form'] = form

    if request.method == 'POST':
        # send out the email
        new_data = request.POST.copy()
        form = SendToFriendForm(new_data)
        if not form.is_valid():
            # the form contains errors
            ctx['form'] = form
        else:
            from blogengine.api.email import send_html_mail
            recipient_list = []
            for item in form.cleaned_data.keys():
                if item.startswith('recipient') \
                and form.cleaned_data[item] != '':
                    recipient_list.append(form.cleaned_data[item])
            from_addr = 'info@gthc.org' # User e-mail addr?
            subject = form.cleaned_data['subject']
            
            # Convert to HTML template and render with mako
            from notmm.utils.template import makoengine
            Loader = makoengine.TemplateLoader(
                directories=settings.TEMPLATE_DIRS,
                #cache_enabled=cache_enabled,
            ) 
            tmpl = Loader.get_template('blogengine/email/tell_a_friend.mako')
            email_body = tmpl.render_unicode(data={
                'message' : form.cleaned_data['message'],
                'obj'     : obj,
                'to'      : form.cleaned_data['recipient1'],
                'sender'  : request.remote_user})
            
            send_html_mail(recipient_list, from_addr, subject, email_body)
            ctx['message'] = 'Mail sent OK!'

    return direct_to_template(request, template_name, extra_context=ctx)

@authorize(RemoteUser(), HTTPUnauthorized)
@decorators.with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def edit(request, **kwargs):
    template_name = kwargs.pop('template_name', 'blogengine/api/edit.mako')

    ctx = dict(message="Welcome, %s"%request.remote_user)
    
    db = request.environ['schevo.db.' + settings.SCHEVO['DATABASE_NAME']]

    # retrieve the object (entity) using the given slug (int)
    obj = EntryManager.objects.find(slug=kwargs['slug'])[0]
    datadict = obj.s.field_map()
    form = EntryForm(data=datadict.value_map())

    ctx['form'] = form
    ctx['title'] = obj.title
    ctx['slug'] = obj._oid
    ctx['oid'] = obj._oid
    if request.method == 'POST':
        # handle classic form validation
        new_data = request.POST.copy()
        form = EntryForm(new_data)
        if not form.is_valid():
            ctx['message'] = 'Found some errors validating the form. Please try again!'
        else:

            tx = obj.t.update()
            #import pdb; pdb.set_trace()
            new_data = form.cleaned_data.copy()
            print new_data
            for item in new_data:
                if item == 'category':
                    c = CategoryManager.objects.get(name=new_data[item])
                    new_data[item] = c
                setattr(tx, item, new_data[item])
            if tx is not None:
                try:
                    db.execute(tx)
                except TransactionFieldsNotChanged:
                    ctx['message'] = 'No changes detected, aborting!'
                else:
                    ctx['message'] = 'Your changes has been saved successfully.'

                ctx['form'] = form
                db.close()

    return direct_to_template(request, template_name, extra_context=ctx)

@authorize(RemoteUser(), HTTPUnauthorized)
@decorators.with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
#@with_db_connection(connection, conf=conf)
def add(request, template_name="blogengine/api/add.mako"):
    form = EntryForm()
    ctx = {
        'form': form,
        'message': 'Use the form below to create a new blog article. When \
        done, hit <b>save</b> to preview your article in a new window.'
    }
    if request.method == 'POST':
        #handle POST request
        new_data = request.POST.copy()
        form = EntryForm(new_data)
        if form.is_valid():
            # Continue with schevo model validation
            
            cleaned_data = form.cleaned_data
            db = request.environ[settings.SCHEVO['DATABASE_NAME']] # schevo.db.blogengine

            # form hack: make the source attribute a filepath and handle the
            # file upload under the scene.. :)

            #try:
            #    cleaned_data['source'] = handle_file_upload(tmpFile)
            #except (IOError, SystemError), e:
            #    raise e
            #else:
            tx = db.BlogEntry.t.create(**cleaned_data)  # create the schevo transaction object
            if tx is not None:
                # model validation fixups
                tx.category = CategoryManager.objects.get(name=cleaned_data['category'])
                tx.pub_date = datetime.now()
                # XXX use a HiddenField perhaps?
                # Must be a valid user
                if request.session.user == 'guest':
                    # Only registered accounts may create blog entries
                    from notmm.utils.wsgi import HTTPUnauthorized
                    message = '''\
<html>
<head>
 <title>Permission denied</title>
</head>
<body>
<h2>Permission denied</h2>
<p>Please <a href="/session_login/">authenticate</a> first. Anonymous blog
posting is not permitted yet. A valid account is required to post new articles.
</p>
<p>Thanks for your understanding and have fun writing stuff... :)</p>
</body>
</html>'''

                    return HTTPUnauthorized(message , mimetype='text/html')
                tx.author = db.Author.findone(username=request.user)
                db.execute(tx)  # execute the transaction/commit
            #db.close()          # close the database IO descriptor
            #ctx['message'] = 'Article (<strong>%s</strong>) created successfully!' % tx.title
            #Session = request.session # NEW session API (0.4.3)
            #Session.add({'message' : 'article saved!'})
            #Session.save()
            from notmm.utils.wsgilib import HTTPRedirectResponse
            return HTTPRedirectResponse('/blog/posts/add/done/')
        else:
            ctx['form'] = form
            ctx['message'] = 'Error saving the new data. Please try again.'

    return direct_to_template(request, template_name, extra_context=ctx)

@authorize(RemoteUser(), HTTPUnauthorized)
@decorators.with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def delete(request, category, slug,
    template_name='blogengine/api/delete.mako'
    ):
    pk_id = 'blogentry_%s'%str(slug)
    #def on_delete_func(request, slug):
    #    obj = get_model(slug)
    #    if obj is not None:
    #        tx = obj.t.delete()
    #        db.execute(tx)
    #
    #if request.method == 'POST':
    #    return on_delete_func(request, slug)
    from blogengine.contrib.api_v1.model import EntryManager
    #from blogengine.forms import DeleteForm
    try:

        obj = EntryManager.objects.get(slug=slug)
    except Exception:
        raise
    else:
        print obj

    ctx = {'form': 'superdeleteform', #DeleteForm(),
           'message': '''\
Hello %s, please select your choices to remove this entry from your blog
roll.''' % request.user,
           'instance': obj,
           'slug': slug}
    return direct_to_template(request, template_name, extra_context=ctx)
