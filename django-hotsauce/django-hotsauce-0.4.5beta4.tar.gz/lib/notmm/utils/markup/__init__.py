"""Misc markup utilities for rendering XML encoded output"""

#from .html import (
#    HTMLPublisher, 
#    MultiDict, 
#    clean_html_document,
#    #convert2markdown
#    )

import html
import html.markdown as md
import html.formutil as formutil

convert2markdown = md.convert2markdown
FormWrapper = formutil.FormWrapper

__all__ = ['html', 'formutil']
