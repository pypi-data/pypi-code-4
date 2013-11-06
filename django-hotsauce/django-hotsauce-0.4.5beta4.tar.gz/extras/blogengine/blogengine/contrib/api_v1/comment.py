import demjson

from datetime import datetime
from functools import wraps
from notmm.utils.wsgilib import HTTPResponse, HTTPRedirectResponse
from notmm.dbapi.orm import with_schevo_database

from blogengine.utils import (
    get_entity_by_string, 
    post_required,
    direct_to_template
    )

from .forms import CommentForm

__all__ = ['render_comment_form', 'preview_comment', 'save_comment']

def render_comment_form(request, **kwargs):

    template_name = "blogengine/comment_form.mako"
    ctx = {'form' : CommentForm()}

    return direct_to_template(request, template_name, extra_context=ctx)

def preview_comment(request, **kwargs):
    status = 401

    if not request.method in ('POST', 'PUT'):
        return render_comment_form(request, **kwargs)
    
    # Process the POST data and return an appropriate
    # notice to the user or redirect..
    # Apparently WebOb thinks this is 'application/xml'.. sigh
    if hasattr(request, 'content_type'):
        request.content_type = 'application/x-www-form-urlencoded'
    
    # Validate the form
    # request.isPOST = True
    if request.method == 'POST':
        new_data = request.POST.copy()
        form = CommentForm(new_data)
        mimetype = 'application/json'
        if form.is_valid():
            # If the form is cleaned from hazardous input, let the user
            # confirm its validity with a form preview then create
            # the entity in the db.
            new_data = getattr(form, 'cleaned_data')
            json = demjson.encode(dict(comment=new_data))
        else:
            # Form needs to be corrected, return it back
            # print 'form contains errors!'
            raw_errors = dict([(name, u"%s" % error[0]) for name, error in \
               form.errors.iteritems() ])
            json = demjson.encode(dict(errordict=raw_errors))
        return HTTPResponse(str(json), mimetype=mimetype, charset='utf-8')
    return HTTPResponse('<p>This view requires a POST request</p>', 
        mimetype='text/html', status=status)

# TODO: add a test case for this view 
# @authorize(RemoteUser())
@with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def save_comment(request, **kwargs):
    """ Save a new comment (POST). """
    db = request.environ[settings.DATABASE_NAME]
    redirect_to = request.session.entry_url
    ctx = {}
    #print redirect_to
    
    #template_name = "blogengine/comment_done.mako"
    form = CommentForm(request.POST.copy())
    if form.is_valid():
        # Save the comment in the DB.. This only works
        # with Schevo for now.
        obj = get_entity_by_string(('slug', kwargs['slug']), db)

        new_data = form.cleaned_data.copy()
        new_data['blogentry'] = obj           # related Entity reference
        new_data['pub_date'] = datetime.now() # XXX: date received
        
        new_data['reviewed'] = settings.BLOGENGINE_DISABLE_MODERATION

        CommentClass = db.extent('Comment')
        try:
            # Create the transaction and save the record
            # in the db.
            tx = CommentClass.t.create(**new_data)
            if tx: 
                # TODO: save a log record in $error_log
                # logger = request.logger
                # logger.info('new comment saved')
                db.execute(tx)
                print 'new comment saved.'
        except:
            raise
        else:
            # Send a email to the admins to validate the comment
            # on line
            pass
    
    return HTTPRedirectResponse(redirect_to)
    #return direct_to_template(request, template_name, **ctx)

save_comment = wraps(post_required)(save_comment)
