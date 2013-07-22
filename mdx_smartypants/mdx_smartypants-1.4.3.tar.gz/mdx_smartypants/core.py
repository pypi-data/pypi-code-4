"""
An extension to Python Markdown that uses smartypants to provide typographically
nicer ("curly") quotes, proper ("em" and "en") dashes, etc.
"""

from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
from mdx_smartypants.spants import smartyPants, Quotes
from namedentities import named_entities

class SmartypantsPost(Postprocessor):
    """
    The smartypants_mdx postprocessor does its heavy lifting here.
    """
    def run(self, text):
        # Must guess language here, before HTML markup added
        if Quotes.direction is None or not Quotes.direction_explicit:
            Quotes.configure_for_text(text)
        return named_entities(smartyPants(text))

class SmartypantsExt(Extension):
    """
    Registers SmartypantsPost as a post processor.
    """
    
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('smartypants', SmartypantsPost(md), '_end')

def makeExtension(configs=None):
    return SmartypantsExt(configs=configs)
