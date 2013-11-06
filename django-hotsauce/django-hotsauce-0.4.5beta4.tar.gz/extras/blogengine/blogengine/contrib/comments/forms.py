#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.forms import (
    CharField, EmailField, Textarea, URLField,
    HiddenInput, Form, BooleanField, HiddenInput
    )

__all__ = ['CommentForm']

# ContactForm = CommentForm
class CommentForm(Form):
    sender_name = CharField(required=True,label='Name')
    sender_email = EmailField(required=True, label='E-mail', \
        help_text='Your e-mail will not be published nor sold to third-parties.')
    sender_message = CharField(required=True, max_length=5000, \
        widget=Textarea(attrs=dict(cols=24)), label='Your comment', \
        help_text='Syntax allowed: Markdown or plain text')
    sender_website = URLField(required=False, label='Your website', \
        help_text='Optional field. Must be a valid URL.')
    
    # Allow commentors to receive an email whenever someone added a new
    # comment
    subscribe_comment_thread = BooleanField(required=False, \
        initial=False, \
        label='Receive e-mail notifications',
        help_text='Subscribe by e-mail to follow-ups ?')

    # blogentry_path = CharField(required=True, widget=HiddenInput())
    

