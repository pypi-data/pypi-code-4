# -*- encoding: utf-8 -*-

from django.contrib import admin

from wysiwyg.comments.models import Comment
from wysiwyg.feed.models import FeedSettings
from wysiwyg.language.models import Language
from wysiwyg.log.models import Log
from wysiwyg.menu.models import MenuItem
from wysiwyg.metadata.models import MetaSet, MetaData
from wysiwyg.pages.models import Page, Post
from wysiwyg.site.models import Site

from wysiwyg.comments.admin import CommentAdmin
from wysiwyg.feed.admin import FeedAdmin
from wysiwyg.language.admin import LanguageAdmin
from wysiwyg.log.admin import LogAdmin
from wysiwyg.menu.admin import MenuItemAdmin
from wysiwyg.metadata.admin import MetaSetAdmin, MetaDataAdmin
from wysiwyg.pages.admin import PageAdmin, PostAdmin
from wysiwyg.site.admin import SiteAdmin

admin.site.register(Comment, CommentAdmin)
admin.site.register(FeedSettings, FeedAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(MetaSet, MetaSetAdmin)
admin.site.register(MetaData, MetaDataAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Site, SiteAdmin)
