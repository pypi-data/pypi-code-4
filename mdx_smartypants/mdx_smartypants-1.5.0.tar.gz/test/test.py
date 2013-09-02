# -*- coding: utf-8 -*-

import markdown
from mdx_smartypants import Quotes
from namedentities import named_entities
from textdata import textlines
import pytest

def tlines(*args, **kwargs):
    kwargs.setdefault('noblanks', False)
    return textlines(*args, **kwargs)

# NB  If one test fails, can prevent rest of testing from having reasonable
# defaults to start with, ergo killing that test too as a cascade of failure.
# Working to make sure each test resets to clean conditions, but that's a work
# in progress.

def compare(md, extensions, answer):
    if isinstance(extensions, str):
        extensions = extensions.split()
    result = markdown.markdown(md, extensions=extensions)
    assert result.strip() == answer.strip()

def test_smartypants():

    text = tlines("""
        Markdown makes HTML from simple text files. But--it lacks typographic
        "prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
        scale'. Now it has it.

        Huzzah!
        """)

    answer = tlines("""
        <p>Markdown makes HTML from simple text files. But&mdash;it lacks typographic
        &ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be sweet. Definitely 7&ndash;8 on a &lsquo;10-point
        scale&rsquo;. Now it has it.</p>
        <p>Huzzah!</p>""")

    compare(text, 'smartypants(entities=named)', answer)


def test_code():
    md = tlines("""
        This is a "paragraph." It should have--nay, needs, typographic pretties.

            def something(a):
                "I am a doc string. I should not be curled"
                print a + ", huh?"  # i am code -- not em-dash safe

        and this is not code. So...make me pretty!
        """)

    answer = tlines("""
        <p>This is a &ldquo;paragraph.&rdquo; It should have&mdash;nay, needs, typographic pretties.</p>
        <pre><code>def something(a):
            "I am a doc string. I should not be curled"
            print a + ", huh?"  # i am code -- not em-dash safe
        </code></pre>
        <p>and this is not code. So&hellip;make me pretty!</p>""")

    compare(md, 'smartypants(entities=named)', answer)


def test_autoguess_direction():
    md = u'هذا "مثال" على هذه المشكلة'
    answer = named_entities(p(u'هذا ”مثال“ على هذه المشكلة'))
    compare(md, 'smartypants(entities=named)', answer)
    assert Quotes.lang == 'ar'

    md = u'א  בְּרֵאשִׁית, בָּרָא אֱלֹהִים, "אֵת" הַשָּׁמַיִם, וְאֵת הָאָרֶץ.'
    answer = named_entities(p(u'א  בְּרֵאשִׁית, בָּרָא אֱלֹהִים, ”אֵת“ הַשָּׁמַיִם, וְאֵת הָאָרֶץ.'))
    compare(md, 'smartypants(entities=named)', answer)
    assert Quotes.lang == 'he'

    md = u'''Yo "dawg," what's happenin'?'''
    answer = named_entities(p(u'''Yo “dawg,” what’s happenin’?'''))
    compare(md, 'smartypants(entities=named)', answer)
    assert Quotes.lang == 'en'


def test_alt_quotes_with_autoguess_directions():
    Quotes.set(sdquo="&laquo;", edquo="&raquo;")
    md = u'''Yo "dawg," what's happenin'?'''
    answer = named_entities(p(u'''Yo «dawg,» what’s happenin’?'''))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.reset()
    Quotes.set(sdquo="&laquo;", edquo="&raquo;", dir='RTL')
    md = u'''Yo "dawg," what's happenin'?'''
    answer = named_entities(p(u'''Yo »dawg,« what&lsquo;s happenin&lsquo;?'''))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.set(dir='LTR')
    answer = named_entities(p(u'''Yo «dawg,» what&rsquo;s happenin&rsquo;?'''))
    compare(md, 'smartypants(entities=named)', answer)

def test_quotes_settings_from_readme():
    Quotes.reset()
    Quotes.set(r'&lasquo;', r'&rasquo;', r'&laquo;', r'&raquo;', dir='LTR')  # Swiss French
    md = u'''"Swiss" 'French'.'''
    answer = p('&laquo;Swiss&raquo; &lasquo;French&rasquo;.')
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.set(r'&sbquo;', r'&lsquo;', r'&bdquo;',  r'&ldquo;', dir='LTR')   # German or Czech
    md = u'''"German" or 'Czech'.'''
    answer = p('&bdquo;German&ldquo; or &sbquo;Czech&lsquo;.')
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.reset()


def p(text):
    return u'<p>' + text + u'</p>'

def test_different_quotes():

    Quotes.set(dir='LTR')
    md = """This is 'rad'!"""
    answer = named_entities(p(u"""This is ‘rad’!"""))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.set(dir='RTL')
    md = """This is 'rad'!"""
    answer = named_entities(p(u"""This is ’rad‘!"""))
    compare(md, 'smartypants(entities=named)', answer)

    # Now repeat, to make sure quote changes are flexible and dynamic

    Quotes.set(dir='LTR')
    md = """This is 'rad'!"""
    answer = named_entities(p(u"""This is ‘rad’!"""))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.set(dir='RTL')
    md = """This is 'rad'!"""
    answer = named_entities(p(u"""This is ’rad‘!"""))
    compare(md, 'smartypants(entities=named)', answer)

    # Now the general case

    Quotes.set('&#8249;', '&#8250;', '&#171;', '&#187;', dir='LTR')
    md = """This "is" 'rad'!"""
    answer = named_entities(p(u"""This «is» ‹rad›!"""))
    compare(md, 'smartypants(entities=named)', answer)

    # another odd case
    Quotes.set('&#x2020;', '&#x2020;', '&#x2021;', '&#x2021;', 'LTR')
    md = """This "is" 'rad'!"""
    answer = named_entities(p(u"""This ‡is‡ †rad†!"""))
    compare(md, 'smartypants(entities=named)', answer)

    # Now back to default
    Quotes.reset()
    md = """This is 'rad'!"""
    answer = named_entities(p(u"""This is ‘rad’!"""))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.reset()


def test_right_to_left():
    """
    Test that quotes are put in the right order in right-to-left
    text.
    """

    Quotes.set(dir='RTL')

    md = u'هذا "مثال" على هذه المشكلة'
    answer = named_entities(p(u'هذا ”مثال“ على هذه المشكلة'))
    compare(md, 'smartypants(entities=named)', answer)

    Quotes.reset()

def test_code_and_pre_some_more():
    """
    Additional tests to insure that handling of code and pre blocks is
    correct. Added based on https://bitbucket.org/jeunice/mdx_smartypants/issue/2/smartypants-educates-text-inside-code
    but have as yet found no cases where mdx_smartypants improperly educates
    """

    extension_pairings = [ ['smartypants(entities=named)'],
                           ['smartypants(entities=named)', 'fenced_code'] ]

    md = tlines("""
        First paragraph

            print "this is some code!"
            print 'these quotes should be straight'
            print '...and that is not a hellip'

        Following paragraph
        """)

    answer = tlines("""
        <p>First paragraph</p>
        <pre><code>print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </code></pre>
        <p>Following paragraph</p>
        """)

    for extensions in extension_pairings:
        compare(md, extensions, answer)

    md2 = tlines("""
        A paragraph

        ~~~~{.python}
        # python code ina fenced code block
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        ~~~~

          - a list
          - items!

        ~~~~.python
        # more python code ina fenced code block (no brackes)
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        ~~~~

        ~~~~.html
        <p>HTML Document...of sorts</p>
        ~~~~
        """)

    answer2 = tlines("""
        <p>A paragraph</p>
        <pre><code class="python"># python code ina fenced code block
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </code></pre>

        <ul>
        <li>a list</li>
        <li>items!</li>
        </ul>
        <pre><code class="python"># more python code ina fenced code block (no brackes)
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </code></pre>

        <pre><code class="html">&lt;p&gt;HTML Document...of sorts&lt;/p&gt;
        </code></pre>
        """)

    compare(md2, ['smartypants(entities=named)', 'fenced_code'], answer2)

    md3 = tlines("""
        final starter para

        <pre>
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </pre>

        middle para

        <code>
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </code>

        last para
        """)

    answer3 = tlines("""
        <p>final starter para</p>
        <pre>
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </pre>

        <p>middle para</p>
        <p><code>
        print "this is some code!"
        print 'these quotes should be straight'
        print '...and that is not a hellip'
        </code></p>
        <p>last para</p>
        """)

    for extensions in extension_pairings:
        compare(md3, extensions, answer3)


def test_entities():
    """
    Ensure that entities are configurable.
    """

    md = tlines("""
        Markdown makes HTML from simple text files. But--it lacks typographic
        "prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
        scale'. Now it has it.""")

    answer = [
        tlines("""
            <p>Markdown makes HTML from simple text files. But&mdash;it lacks typographic
            &ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be sweet. Definitely 7&ndash;8 on a &lsquo;10-point
            scale&rsquo;. Now it has it.</p>"""),
        tlines("""
            <p>Markdown makes HTML from simple text files. But&#8212;it lacks typographic
            &#8220;prettification.&#8221; That&#8230; That&#8217;d be sweet. Definitely 7&#8211;8 on a &#8216;10-point
            scale&#8217;. Now it has it.</p>"""),
        tlines(u"""
            <p>Markdown makes HTML from simple text files. But—it lacks typographic
            “prettification.” That… That’d be sweet. Definitely 7–8 on a ‘10-point
            scale’. Now it has it.</p>"""),
        tlines("""
            <p>Markdown makes HTML from simple text files. But&#8212;it lacks typographic
            &#8220;prettification.&#8221; That&#8230; That&#8217;d be sweet. Definitely 7&#8211;8 on a &#8216;10-point
            scale&#8217;. Now it has it.</p>"""),
    ]

    for i, entities in enumerate(['named', 'numeric', 'unicode', 'none']):
        compare(md, 'smartypants(entities=' + entities + ')', answer[i])

def test_issue2():
    """
    Check the problem identified by issue 2, excess wrapping of Unicode characters
    in HTML entities.
    """

    md = tlines(u"""
        ~~~~
        .
        ├── deployment/
        │   ├── ansible
        │   ├── deploy.yml
        │   ├── files/
        ~~~~
        """)

    answer = tlines(u"""
        <pre><code>.
        ├── deployment/
        │   ├── ansible
        │   ├── deploy.yml
        │   ├── files/
        </code></pre>
        """)

    compare(md, 'smartypants fenced_code', answer)

    answer = tlines(u"""
        <pre><code>.
        &#9500;&#9472;&#9472; deployment/
        &#9474;   &#9500;&#9472;&#9472; ansible
        &#9474;   &#9500;&#9472;&#9472; deploy.yml
        &#9474;   &#9500;&#9472;&#9472; files/
        </code></pre>
        """)

    compare(md, 'smartypants(entities=named) fenced_code', answer)
