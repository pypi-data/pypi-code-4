from quoter import *
import pytest

def test_braces():
    assert braces('this') == '{this}'
    assert braces('this', padding=1) == '{ this }'
    assert braces('this', margin=1) == ' {this} '
    assert braces('this', padding=1, margin=1) == ' { this } '

def test_brackets():
    assert brackets('this') == '[this]'
    assert brackets('this', padding=1) == '[ this ]'
    assert brackets('this', margin=1) == ' [this] '
    assert brackets('this', padding=1, margin=1) == ' [ this ] '

#def test_chars():
#    percent = Quoter(chars='%%')
#    assert percent('something') == '%something%'
#    doublea = Quoter(chars='<<>>')
#    assert doublea('AAA') == '<<AAA>>'

def test_shortcuts():
    assert ' '.join([qs('one'), qd('two'), qb('and'), qt('three')]) == \
        "'one' \"two\" `and` \"\"\"three\"\"\""

def test_instant():
    assert Quoter('+[ ', ' ]+')('castle') == '+[ castle ]+'

def test_lambda():
    f = lambda v: ('(', abs(v), ')') if v < 0 else ('', v, '')
    financial = LambdaQuoter(f)
    assert financial(-10) == '(10)'
    assert financial(44)  == '44'

    password = LambdaQuoter(lambda v: ('', 'x' * len(v), ''))
    assert password('secret!') == 'xxxxxxx'

    wf = lambda v:  ('**', v, '**') if v < 0 else ('', v, '')
    warning = LambdaQuoter(wf, name='warning')
    assert warning(12) == '12'
    assert warning(-99) == '**-99**'
    assert warning(-99, padding=1) == '** -99 **'

    assert lambdaq.warning(12) == '12'
    assert lambdaq.warning(-99) == '**-99**'
    assert lambdaq.warning(-99, padding=1) == '** -99 **'


def test_examples():
    assert single('this') == "'this'"
    assert double('that') == '"that"'
    assert backticks('ls -l') == "`ls -l`"
    assert braces('curlycue') == "{curlycue}"

    bars = Quoter('|')
    assert bars('x') == '|x|'

    plus = Quoter('+', '')
    assert plus('x') == '+x'

    variable = Quoter('${', '}', name='variable')
    assert variable('x') == '${x}'

def test_attribute_invocations():
    assert single('something') == quote.single('something')
    assert single('something', margin=2, padding=3) == quote.single('something', margin=2, padding=3)
    assert braces('b') == quote.braces('b')

    # now test wholesale
    names = 'braces brackets angles parens qs qd qt qb single double triple ' +\
            'backticks anglequote guillemet curlysingle curlydouble'
    for name in names.split():
        main = eval(name)
        attr = eval('quote.' + name)
        assert main is attr
        assert main('string') == attr('string')

def test_quote_shortcut():
    variable = Quoter('${', '}', name='variable')
    assert variable('x') == '${x}'


    assert quote('myvar', style='variable') == '${myvar}'

    assert quote('this', style='braces') == '{this}'

def test_redef():
    braces = Quoter('{', '}', padding=1, name='braces')
    assert braces('this') == '{ this }'
    assert braces('this', padding=0) == '{this}'


def test_para():
    para = HTMLQuoter('p')
    # assert para('this is great!', {'class':'emphatic'}) == "<p class='emphatic'>this is great!</p>"
    assert para('this is great!', '.emphatic') == "<p class='emphatic'>this is great!</p>"
    assert para('First para!', '#first') == "<p id='first'>First para!</p>"

    para_e = HTMLQuoter('p.emphatic')
    assert para_e('this is great!') == "<p class='emphatic'>this is great!</p>"
    assert para_e('this is great?', '.question') == "<p class='question'>this is great?</p>"

    br = HTMLQuoter('br', void=True)
    assert br() == '<br>'

    para = HTMLQuoter('p', attquote=double)
    assert para('this is great!', {'class':'emphatic'}) == '<p class="emphatic">this is great!</p>'

    div = HTMLQuoter('div', attquote=double)
    assert div('something', '.todo') == '<div class="todo">something</div>'

def test_xml_examples():
    item = XMLQuoter(tag='item', ns='inv', name='item inv_item')
    assert item('an item') == '<inv:item>an item</inv:item>'
    assert xml.item('another') == '<inv:item>another</inv:item>'
    assert xml.inv_item('yet another') == '<inv:item>yet another</inv:item>'
    assert xml.thing('something') == '<thing>something</thing>'


def test_xml_auto_and_attributes():

    assert xml.root('this') == '<root>this</root>'
    assert xml.root('this', ns='one') == '<one:root>this</one:root>'
    assert xml.branch('that') == '<branch>that</branch>'
    assert xml.branch('that', ns='two') == '<two:branch>that</two:branch>'

    assert xml.comment('hidden') == '<!--hidden-->'

def test_html_auto_and_attributes():
    assert html.b('bold') == '<b>bold</b>'
    assert html.emphasis('bold') == '<emphasis>bold</emphasis>'
    assert html.strong('bold') == '<strong>bold</strong>'
    assert html.strong('bold', padding=1) == '<strong> bold </strong>'
    assert html.strong('bold', margin=1) == ' <strong>bold</strong> '

    assert html.comment('XYZ') == '<!--XYZ-->'
    assert html.comment('XYZ', padding=1) == '<!-- XYZ -->'
