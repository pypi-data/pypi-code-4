#!/usr/bin/python
# -*- coding: utf-8 -*-
#    ******  The Cloud Toolbox v0.1.2******
#    This is the cloud toolbox -- a single module used in several packages
#    found at <https://github.com/cloudformdesign>
#    For more information see <cloudformdesign.com>
#
#    This module may be a part of a python package, and may be out of date.
#    This behavior is intentional, do NOT update it.
#    
#    You are encouraged to use this pacakge, or any code snippets in it, in
#    your own projects. Hopefully they will be helpful to you!
#        
#    This project is Licenced under The MIT License (MIT)
#    
#    Copyright (c) 2013 Garrett Berg cloudformdesign.com
#    An updated version of this file can be found at:
#    <https://github.com/cloudformdesign/cloudtb>
#    
#    Permission is hereby granted, free of charge, to any person obtaining a 
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation 
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the 
#    Software is furnished to do so, subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#    
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
#    DEALINGS IN THE SOFTWARE.
#
#    http://opensource.org/licenses/MIT
# -*- coding: utf-8 -*-

import pdb

import sys

import unittest
import re

import bs4
from PyQt4 import QtGui

try:
    from .. import textools
    from ..extra import richtext, researched_richtext
    from .. import dectools
except ValueError:
    for n in xrange(2):
        try:
            import textools
            from extra import richtext, researched_richtext
            import dectools
            break
        except ImportError:
            import sys
            sys.path.insert(1, '..')
    else:
        raise ImportError
        
DEBUG = True


def text_setUp(self):
    # Note that all texts have a new line at the end
    # setup text 1
    text1 = '''talking about expecting the Spanish Inquisition in the \
text below: 
Chapman: I didn't expect a kind of Spanish Inquisition. 
(JARRING CHORD - the cardinals burst in) 
Ximinez: NOBODY expects the Spanish Inquisition! Our chief weapon is \
surprise...surprise and fear...fear and surprise.... Our two weapons are \
fear and surprise...and ruthless efficiency.... Our *three* weapons are fear, \
surprise, and ruthless efficiency...and an almost fanatical devotion to the \
Pope.... Our *four*...no... *Amongst* our weapons.... Amongst our weaponry... \
are such elements as fear, surprise.... I'll come in again. (Exit and exeunt) 
'''
    text1_proper_formatted = '''<*m0>[[{talking {about }<g[1]>expect{ing }<g[2]>{the }<g[3]>Spanish Inquisition{ }<g[4]>}<g[0]>]]in the text below: 
Chapman: <*m1>[[{I {didn't }<g[1]>expect{ a kind of }<g[2]>Spanish Inquisition{.}<g[4]>}<g[0]>]] 
(JARRING CHORD - the cardinals burst in) 
Ximinez: <*m2>[[{{NOBODY }<g[1]>expect{s }<g[2]>{the }<g[3]>Spanish Inquisition{!}<g[4]>}<g[0]>]] Our chief weapon is surprise...surprise and fear...fear and surprise.... Our two weapons are fear and surprise...and ruthless efficiency.... Our *three* weapons are fear, surprise, and ruthless efficiency...and an almost fanatical devotion to the Pope.... Our *four*...no... *Amongst* our weapons.... Amongst our weaponry... are such elements as fear, surprise.... I'll come in again. (Exit and exeunt) 
'''
    text1_proper_replaced = '''<*m0>[[{talking {about }<g[1]>expect{ing }<g[2]>{the }<g[3]>Spanish Inquisition{ }<g[4]>}<g[0]>]]==>[[What is this, the Spanish Inquisition?]]in the text below: 
Chapman: <*m1>[[{I {didn't }<g[1]>expect{ a kind of }<g[2]>Spanish Inquisition{.}<g[4]>}<g[0]>]]==>[[What is this, the Spanish Inquisition?]] 
(JARRING CHORD - the cardinals burst in) 
Ximinez: <*m2>[[{{NOBODY }<g[1]>expect{s }<g[2]>{the }<g[3]>Spanish Inquisition{!}<g[4]>}<g[0]>]]==>[[What is this, the Spanish Inquisition?]] Our chief weapon is surprise...surprise and fear...fear and surprise.... Our two weapons are fear and surprise...and ruthless efficiency.... Our *three* weapons are fear, surprise, and ruthless efficiency...and an almost fanatical devotion to the Pope.... Our *four*...no... *Amongst* our weapons.... Amongst our weaponry... are such elements as fear, surprise.... I'll come in again. (Exit and exeunt) 
'''
    regexp1 = (r'''([a-zA-Z']+\s)+?expect(.*?)(the )*Spanish ''' + 
                    r'''Inquisition(!|.)''')
    replace1 = r'What is this, the Spanish Inquisition?'
    
    # setup text 2
    text2 = ('''Researching my re search is really easy with this handy new tool! 
It shows me my matches and group number, I think it is great that they're seen\
 in this new light! 
''')
    text2_proper_formatted = '''<*m0>[[{{R}<g[2]>esearching}<g[0, 1]>]] my <*m1>[[{{r}<g[2]>e search}<g[0, 1]>]] <*m2>[[{is}<g[0, 3]>]] really easy with <*m3>[[{{{t}<g[5]>h}<g[4]>is}<g[0, 3]>]] handy new tool! 
It shows me my matches and group number, I think it <*m4>[[{is}<g[0, 3]>]] great that they'<*m5>[[{{r}<g[2]>e seen}<g[0, 1]>]] in <*m6>[[{{{t}<g[5]>h}<g[4]>is}<g[0, 3]>]] new light! 
'''
    text2_proper_replaced = '''<*m0>[[{{R}<g[2]>esearching}<g[0, 1]>]]==>[[New Research!]] my <*m1>[[{{r}<g[2]>e search}<g[0, 1]>]]==>[[New Research!]] <*m2>[[{is}<g[0, 3]>]]==>[[New Research!]] really easy with <*m3>[[{{{t}<g[5]>h}<g[4]>is}<g[0, 3]>]]==>[[New Research!]] handy new tool! 
It shows me my matches and group number, I think it <*m4>[[{is}<g[0, 3]>]]==>[[New Research!]] great that they'<*m5>[[{{r}<g[2]>e seen}<g[0, 1]>]]==>[[New Research!]] in <*m6>[[{{{t}<g[5]>h}<g[4]>is}<g[0, 3]>]]==>[[New Research!]] new light! 
'''
    regexp2 = r'''((R|r)e ?se\w*)|(((T|t)h)?is)'''
    replace2 = r'New Research!'
    
    text3 = ('''This is a paragraph with several lines between everything.

I have had some serious problems with this in the past.



Let's see if it works.''')
    text3_proper_formatted = ('''This is a paragraph with <*m0>[[{several lines}<g[0]>]] between everything.

I have had some <*m1>[[{serious}<g[0]>]] problems with this in the past.



Let's see if it works.''')
    text3_proper_replaced = ('''This is a paragraph with <*m0>[[{several lines}<g[0]>]]==>[[NEW WORDS]] between everything.

I have had some <*m1>[[{serious}<g[0]>]]==>[[NEW WORDS]] problems with this in the past.



Let's see if it works.''')
    regexp3 = r'''several lines|serious'''
    replace3 = 'NEW WORDS'
    
    self.text_list = (text1, text2, text3)
    self.regexp_list = (regexp1, regexp2, regexp3)
    self.replace_list = (replace1, replace2, replace3)
    self.proper_formatted = (text1_proper_formatted, text2_proper_formatted,
                             text3_proper_formatted)
    self.proper_replaced = (text1_proper_replaced, text2_proper_replaced,
                            text3_proper_replaced)
    self.all_list = tuple(zip(self.text_list, self.regexp_list, 
                              self.replace_list,
                              self.proper_formatted, self.proper_replaced))

def get_researched_str_recursive(data_list):
    outlist = []
    for regpart in data_list:
        if type(regpart) == str:
            outlist.append(regpart)
        else:
            outlist.append(get_researched_str_recursive(regpart.data_list))
    return ''.join(outlist)

class regPartTest(unittest.TestCase):
#    maxDiff = None
    
    def setUp(self):
        text_setUp(self)
        app = QtGui.QApplication(sys.argv)
        self.TextEdit = QtGui.QTextEdit()
        self.TextEdit.setText(self.text_list[0])
    
    @dectools.debug(DEBUG)
    def test_re_search(self):
        for stuff in self.all_list:
            text, regexp, replace, prop_formatted, prop_replaced = stuff
            del stuff
            
            regcmp = re.compile(regexp)
            researched = textools.re_search(regexp, text)
            r_formatted = textools.format_re_search(researched)
            r_text = textools.get_str_researched(researched)
            self.assertEqual(r_text, text, 'Simple text not equal')
            self.assertEqual(r_formatted, prop_formatted, 'Formatted')
            # uncomment these if something in formatting changes to
            # print the changes
#            print 'PROPER FORMAT'
#            print r_formatted
#            print 'END PROPER'
#            print
            
            # go into a little more depth than just pulling the .text
            # attribute...
            r_text = get_researched_str_recursive(researched)
            self.assertEqual(r_text, text, 'Recursive text not equal')
            
            # testing substitutions
            researched_replace = textools.re_search_replace(researched, 
                                            replace, preview = True)
            std_replaced = regcmp.sub(replace, text)
            r_replaced = textools.get_str_researched(researched_replace)
            r_formatted_replaced = textools.format_re_search(
                                                        researched_replace)
            
#            print 'PROPER REPLACED'
#            print r_formatted_replaced
#            print 'END REPLACED'
#            print
            
            self.assertEqual(r_formatted_replaced, prop_replaced)
            self.assertEqual(r_replaced, std_replaced, 
                             'Replaced text not equal')

    @dectools.debug(DEBUG)
    def test_richtext(self):
        '''Test the richtext position finder. This also simultaniously tests
        to make sure that most of the richtext and researched_richtext
        modules are working properly'''
        for stuff in self.all_list:
            text, regexp, replace, prop_formatted, prop_replaced = stuff
            del stuff
            
            researched = textools.re_search(regexp, text)
            
            # get the researched_html_list. This is the primary list we will
            # be using throughout.
            researched_html_list = researched_richtext.re_search_format_html(
                researched)
            
            # get straight html
            str_html = richtext.get_str_formated_html(researched_html_list)
            
            # use beautiful soup to make sure we are formatting into correct
            # html
#            soup = bs4.BeautifulSoup(str_html)
#            self.assertEqual(str(soup), str_html, 'Html improperly formatted')
#            del soup
            
            # use the get_position to ensure that everything is being kept
            # track of properly. This tests a whole range of issues, ensuring
            # that pretty much every part of the object is being properly
            # tracked.
            ignore = set((n[0] for n in richtext.html_replace_str_list))
            deformated_html_list = richtext.deformat_html(str_html, keepif = 
                richtext.KEEPIF['black-bold'])
            
            str_deformated = richtext.get_str_formated_html(
                deformated_html_list)
            
            # it doesn't matter if the lists are identical, all that matters
            # is that the position function works the same.
            # checks to make sure that the position function works on both
            # lists
            for check_list, check_str in ((researched_html_list, str_html),
                               (deformated_html_list, str_deformated)):
                num_ignores = 0
                for n in xrange(0, len(check_str)):
                    new_n = n - num_ignores
                    if text[new_n] in ignore:
                        num_ignores += 1
                        continue
                    out_text_pos, out_vis_pos, out_html_pos = (
                        richtext.get_position(check_list, true_position = 
                        new_n))
                    self.assertEqual(text[n], check_str[out_html_pos], 
                    "Position {0}"
                        " not equal:\nTEXT[n:n+10] == {1}\n\nHTML[pos:pos+50]"
                        "== {2}".format(n, text[n:n+10], 
                                        check_str[out_html_pos:
                                                out_html_pos+50]))
                    



            
            # TODO: I'm not sure if this needs to work. Currently it doesn't
#            self.assertEqual(str_deformated, str_html)
        
                
class qtTextTest(unittest.TestCase):
    def setUp(self):
        text_setUp(self)
        app = QtGui.QApplication(sys.argv)
        self.TextEdit = QtGui.QTextEdit()
        self.TextEdit.setText(self.text_list[0])

    def test_position(self):
        for stuff in self.all_list:
            text, regexp, replace, prop_formatted, prop_replaced = stuff
            del stuff
            plain_text_html = richtext.get_str_plain_html(text)
            self.TextEdit.setText(plain_text_html)
            rawtext = self.TextEdit.toPlainText()
            assert(rawtext == text)
            self.TextEdit.setHtml(str_html)
            qt_visual = self.TextEdit.toPlainText()
            # using already gotten deformatted_html_list
            for n in xrange(len(rawtext)):
                tc = self.TextEdit.textCursor()
                tc.setPosition(n)
                self.TextEdit.setTextCursor(tc)
                
                get_pos = self.TextEdit.textCursor().position()
                self.assertEqual(get_pos, n, "How is the position different?")
                
                def_text_pos, def_vis_pos, def_html_pos = (
                    richtext.get_position(deformated_html_list, 
                            visible_position = n))
                self.assertEqual(def_vis_pos, n)
        
if __name__ == '__main__':
    unittest.main()
    