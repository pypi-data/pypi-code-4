# -*- coding: utf-8 -*-

import markdown
from mdx_smartypants import Quotes
from namedentities import named_entities
import pytest

# import mdx_smartypants

def test_smartypants():
    
    text = """
Markdown makes HTML from simple text files. But--it lacks typographic
"prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
scale'. Now it has it.

Huzzah!
"""

    answer = """
<p>Markdown makes HTML from simple text files. But&mdash;it lacks typographic
&ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be sweet. Definitely 7&ndash;8 on a &lsquo;10-point
scale&rsquo;. Now it has it.</p>
<p>Huzzah!</p>
"""
    result = markdown.markdown(text, extensions=['smartypants'])
   
    assert result.strip() == answer.strip()


def test_code():
    md = """
This is a "paragraph." It should have--nay, needs, typographic pretties.

    def something(a):
        "I am a doc string. I should not be curled"
        print a + ", huh?"  # i am code -- not em-dash safe

and this is not code. So...make me pretty!
"""

    result = markdown.markdown(md, extensions=['smartypants'])
    
    answer = """
<p>This is a &ldquo;paragraph.&rdquo; It should have&mdash;nay, needs, typographic pretties.</p>
<pre><code>def something(a):
    "I am a doc string. I should not be curled"
    print a + ", huh?"  # i am code -- not em-dash safe
</code></pre>
<p>and this is not code. So&hellip;make me pretty!</p>
"""
    
    assert result.strip() == answer.strip()
    
def test_autoguess_direction():
    md = u'هذا "مثال" على هذه المشكلة'
    answer = named_entities(u'هذا ”مثال“ على هذه المشكلة')
    result = markdown.markdown(md, extensions=['smartypants'])
    assert Quotes.lang == 'ar'
    assert result.strip() == p(answer.strip())
    
    md = u'א  בְּרֵאשִׁית, בָּרָא אֱלֹהִים, "אֵת" הַשָּׁמַיִם, וְאֵת הָאָרֶץ.'
    answer = named_entities(u'א  בְּרֵאשִׁית, בָּרָא אֱלֹהִים, ”אֵת“ הַשָּׁמַיִם, וְאֵת הָאָרֶץ.')
    result = markdown.markdown(md, extensions=['smartypants'])
    assert Quotes.lang == 'he'
    assert result.strip() == p(answer.strip())
    
    md = u'''Yo "dawg," what's happenin'?'''
    answer = named_entities(u'''Yo “dawg,” what’s happenin’?''')
    result = markdown.markdown(md, extensions=['smartypants'])
    assert Quotes.lang == 'en'
    assert result.strip() == p(answer.strip())


def p(text):
    return '<p>' + text + '</p>'

def test_different_quotes():
    
    Quotes.set(dir='LTR')
    md = """This is 'rad'!"""
    answer = u"""This is ‘rad’!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))

    Quotes.set(dir='RTL')
    md = """This is 'rad'!"""
    answer = u"""This is ’rad‘!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))

    # Now repeat, to make sure quote changes are flexible and dynamic
    
    Quotes.set(dir='LTR')
    md = """This is 'rad'!"""
    answer = u"""This is ‘rad’!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))

    Quotes.set(dir='RTL')
    md = """This is 'rad'!"""
    answer = u"""This is ’rad‘!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))
   
    # Now the general case
    
    Quotes.set('&#8249;', '&#8250;', '&#171;', '&#187;', dir='LTR')
    md = """This "is" 'rad'!"""
    answer = u"""This «is» ‹rad›!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))
    
    # another odd case
    Quotes.set('&#x2020;', '&#x2020;', '&#x2021;', '&#x2021;', 'LTR')
    md = """This "is" 'rad'!"""
    answer = u"""This ‡is‡ †rad†!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))
    
    # Now back to default
    Quotes.reset()
    md = """This is 'rad'!"""
    answer = u"""This is ‘rad’!"""
    result = markdown.markdown(md, extensions=['smartypants'])
    assert named_entities(result) == named_entities(p(answer))
 
    
def test_right_to_left():
    """
    Test that quotes are put in the right order in right-to-left
    text.
    """
    
    Quotes.set(dir='RTL')
    
    md = u'هذا "مثال" على هذه المشكلة'
    answer = named_entities(u'هذا ”مثال“ على هذه المشكلة')
    
    result = markdown.markdown(md, extensions=['smartypants'])
    assert result.strip() == p(answer.strip())
    
    Quotes.set(dir='LTR') # back to normal defaults