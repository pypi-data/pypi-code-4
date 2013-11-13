#!/usr/bin/python
# -*- coding: utf-8 -*-
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2.21
#     Copyright 2013 Garrett Berg
#     
#     Loosly based on LaTeX2WP version 0.6.2, Luca Trevisan Copyright 2009
#    
#     This file is part of wordtex, a program that converts
#     a LaTeX document into a format that is ready to be
#     copied and pasted into WordPress.
#    
#     You are free to redistribute and/or modify wordtex under the
#     terms of the GNU General Public License (GPL), version 3
#     or (at your option) any later version.
#    
#     You should have received a copy of the GNU General Public
#     License along with wordtex.  If you can't find it,
#     see <http://www.gnu.org/licenses/>

'''


##############
## Changing font type to courier new (should work)
# I just need to add the following around the block
# I think the "style = "padd..." could be replaced with the std indent
# STILL NEED TO CHECK IN WP
<p style="padding-left: 30px;"><span style="font-family: comic sans ms,sans-serif; background-color: #c0c0c0; color: #000000;">This is an example of the kind of output I want for my code
Note that it is indented, of a different font, and has a different background color.</span>
'''
#TODO: Need colors and tables
#TODO: need math
range = xrange
import pdb

import re
import copy

import texlib
from cloudtb import textools


## Feel Free to change these things if you want
SECTION_NAME = ""
SUBSECTION_NAME = ""


# keeps track of section number in document
SECTION_NUMBER = 0
SUBSECTION_NUMBER = 0
PARAGRAPH = ('<p>', '</p>')
###############################
### Call functions for formatting
def delete_self(texpart, *args, **kwargs):
    texpart.text_data = ['']

def section_num(texpart, *args, **kwargs):
    global SECTION_NUMBER
    SECTION_NUMBER += 1
    texpart.text_data.insert(0, SECTION_NAME + ' {0}: '.format(
        SECTION_NUMBER))
    texpart.text_data = texlib.reform_text(texpart.text_data, 
                                           no_indicators= True)

def subsection_num(texpart, *args, **kwargs):
    global SUBSECTION_NUMBER
    SUBSECTION_NUMBER += 1
    texpart.text_data.insert(0, SUBSECTION_NAME + ' {0}.{1}: '.format(
        SECTION_NUMBER, SUBSECTION_NUMBER))
    texpart.text_data = texlib.reform_text(texpart.text_data, 
                                           no_indicators= True)

def href_call(texpart, *args, **kwargs):
    hlink = re.match(r'\\href\{(.*?)}', texpart.start_txt).group(1)
    html_start, html_end = texpart.add_outside
    html_start = html_start.format(hlink)
    texpart.add_outside = html_start, html_end

class list_call(object):
    def __init__(self, enumerate = False):
        self.enumerate = enumerate
        self.count = 1
    
    def __call__(self, texpart, *args, **kwargs):
        '''Have to do a call here only because the "item"s may or may not have
        an end point (particularily the last one). Have to create a start and stop 
        so it can be handled by process_inout'''
        
        # have to handle itemize and enumerate first for nested lists
        use_dict = {'itemize': begin_dict['itemize'],
                    'enumerate': begin_dict['enumerate']}
        texpart.no_update_text = False
        texpart.update_text(use_dict)
        regexp = re.compile(r'\\item ([\w\W]*?)(?=(\\item|$))')
        researched = []
        for n in texpart.text_data:
            if type(n) in (str, unicode):
#                pdb.set_trace()
                researched.extend(textools.re_search(regexp, n))
            else:
                researched.append(n)
        new_body = []
        for text in researched:
            if type(text) in (str, unicode, texlib.TexPart):
                new_body.append(text)
            else:
                self.count += 1
                assert( r'\end{itemize}' not in text.group(1))
                new_body.append(r'\startitem ' + text.group(1) + r'\enditem ')
#                need = r'\end{itemize}'
#                if need in text.text:
#                    new_body.append(text.text[text.text.find(need):])
        texpart.text_data = texlib.reform_text(new_body, no_indicators = True)
        
        line_items = [
        ['item'         ,tp(add_outside = ('<li>','</li>'), 
                        no_outer_pgraphs = True)],
        ]
        use_dict = build_dict('list_call', line_items, r'\\start{0} ', None, 
                              r'\\end{0}')
        texpart.update_text(use_dict = use_dict)
        texpart.update_text()
    
class tabularnewline_call(object):
    '''Class which accepts default row settings'''
    def __init__(self, textpart_list):
        self.textpart_list = textpart_list
    
    def __call__(self, texpart, *args, **kwargs):
        body, = texpart.text_data
#        if 'Bachelor' in body:
#            pdb.set_trace()
        columns = re.split(' [&] ', body)
        col_st, col_end = '\\tabcolstart ', ' \\tabcolend\n'
        columns = [col_st + n + col_end for n in columns]
        Tparts = []
        for i, tpart in enumerate(self.textpart_list):
            tpart.update_match_re(([r'\\tabcolstart '], [], 
                                   [r' \\tabcolend\n']))
            Tparts.extend(texlib.get_text_data([columns[i]], tpart))
        texpart.no_update_text = False        
        texpart.text_data = Tparts
        texpart.update_text()

def _tabular_get_column_list(start_txt):
    get_columns_raw = r'\\begin{tabular\*?}{(.*)}'
    get_split_columns = r'\|'
    # TODO: What do 'p' and 'm' stand for?
    get_column_info = r'>{\\(.*?)}[pm]{([0-9.]*)(\\?[\w]*)}'    
    
    raw_cols = re.match(get_columns_raw, start_txt).group(1)
    split_cols = re.split(get_split_columns, raw_cols)
    default_align = 'raggedright'
    default_width = (1, 'DEFAULT')
    align_data, width_data = [], []
    for col in split_cols:
        if col == '':
            continue
        if col == 'c':
            align_data.append(default_align)
            width_data.append(default_width)
        else:
            cgroup = re.match(get_column_info, col).group
            align_data.append(cgroup(1))
            width_data.append((float(cgroup(2)), cgroup(3)))
#    pdb.set_trace()
    align_dict = {'raggedright' : 'left',
                  'centering'   : 'center'
                 }
    for i, value in enumerate(align_data):
        align_data[i] = align_dict[value]
    
    perc_width_format = ('style="width: {0}%; border: 1px solid #cccccc; '
                        'padding:0px 5px;"')
    # we are going to do this better in the future
    tot_width = sum([n[0] for n in width_data])
    last_type = -1
    for i, value in enumerate(width_data):
        amount, ctype = value
        if last_type != -1:
            assert(ctype == last_type)  # doing this for now.
        
        amount = int(amount * 100.0 / tot_width)
        # TODO: more dynamic possibilities for width data
        width_data[i] = perc_width_format.format(amount)
    
    td_format = r'<td align="{col_align}" valign="{row_align}" {width}>'
    textpart_list = []
    for i, align in enumerate(align_data):
        Tpart = texlib.TexPart(
                add_outside = (td_format.format(col_align = align,
                                            row_align = 'top',
                                            width = width_data[i]), 
                                '</td>'),
                no_outer_pgraphs = True,
            )
            
#        Tpart.update_match_re([])
        Tpart.label = 'tabular_column_custom dict:tabular_call'
        textpart_list.append(Tpart)
    return textpart_list

def tabular_call(texpart, *args, **kwargs):
    '''Handles formating tables.'''
#    For developers: gives some good insight into
#    how to reach into the depths of this api. Note that this function is
#    a "call_first" function (see "begin_objects" below), and that it
#    recieved non-updated text
    textpart_list = _tabular_get_column_list(texpart.start_txt)
#    pdb.set_trace()
    # the \tabularnewline syntax has to be changed as it is not compatitble
    #  with the convert_inout function in texlib
    body, = texpart.text_data
    # Just remove \hline for now
    body = re.sub(r'\\hline ?\n?', '', body)
    tab_st, tab_end = '\\tabrowstart ', ' \\tabrowend\n'
    split = body.split('\\tabularnewline\n')
    assert(split[-1] == '' or split[-1].find("\\hline ") == 0)
    del split[-1]
    new_body = [tab_st + n + tab_end for n in split]
    texpart.text_data = [''.join(new_body)]
    
    # constructing custom dictionary for use in update_text
    tpart = texlib.TexPart(
                add_outside = ('<tr>','</tr>'),
                call_first = tabularnewline_call(textpart_list),
                no_update_text = True,
                no_outer_pgraphs = True)
    
    
    tpart.update_match_re(([r'\\tabrowstart '], [], [r' \\tabrowend\n']))
    tpart.label = 'tabrow' + ' function: ' + 'tabular_call'
    use_dict = {'tabularnewline' : tpart}
    
    # The "no_update_text" flag must be set to False so that the below can
    #  work fully
    # a custom dictionary must be created and fed to update_text
    # finally the text must be updated normally
    texpart.no_update_text = False 
    texpart.update_text(use_dict = use_dict)
    

########################
## Automatically creating dictionaries of regexp's
tp = texlib.TexPart
# TODO: make label store the dictionary it is from
def build_dict(name, patterns, 
               inside_template = None, start_template = None, 
               end_template = None, custom = None):
    mydict = {}
    i = 0
    for p, texpart in patterns:
        if custom != None:
            i += 1
            inside, start, end = p
            p = 'i {0}:{1}:{2}'.format(i, inside, start, end)
        else:
            if inside_template == None:
                inside = []
            else:
                if type(inside_template) in (str, unicode):
                    inside = [inside_template.format(p)]
                else:
                    inside = inside
            if start_template == None: 
                start = []
            else:
                start = [start_template.format(p)]
            if end_template == None:
                end = []
            else:
                end = [end_template.format(p)]
        
        new_tp = copy.copy(texpart)
        new_tp.update_match_re((inside, start, end))
        new_tp.label = p + ' dict:' + name
        mydict[p] = new_tp
    return mydict

# Create a dict of begin objects
begin_objects = [
['document'     ,tp()                                                  ],
['tabular\*?'      ,tp(call_first = tabular_call,
                    add_outside = ('<table>','</table>'),
                    no_outer_pgraphs = True,
                    no_update_text = True)], 
['lstlisting'   ,tp(add_outside = ('<ul><pre>','</pre></ul>'),
                    no_update_text = True, no_std_format = True,
                    no_outer_pgraphs=True)],
['itemize'      ,tp(add_outside = ('<ul>', '</ul>'),
                    no_outer_pgraphs = True,
                    no_update_text = True,
                    call_first = list_call(),)],
['enumerate'    ,tp(add_outside = ('<ol>','</ol>'),
                    no_outer_pgraphs = True,
                    no_update_text = True,
                    call_first = list_call(enumerate = True))],
['equation'     ,tp(add_outside = ('','' ) )], #TODO: need basic equation
]

begin_dict = build_dict('begin', begin_objects, 
                           r'\\begin\{{{0}}}(\{{.*}})? *?', None,
                           r'\\end\{{{0}}} *?')

# Create a dict for ifs

if_objects = [
['blog'      , tp(no_outer_pgraphs = True)],
['tex'       , tp(call_first = delete_self,
                  no_outer_pgraphs = True)],
['false'     , tp(call_first = delete_self,
                  no_outer_pgraphs = True)]
]

if_dict = build_dict('if', if_objects, r'\\if{0} ', 
                        r'\\if.*? ', 
                        r'\\fi ')


txt_attributes = [
['textbf'   ,tp(add_outside = ('<strong>', '</strong>'),
                no_outer_pgraphs = True)],# bolded
['textit'   ,tp(add_outside = ('<em>', '</em>'),
                no_outer_pgraphs = True)],# italicized
['uline'    ,tp(add_outside = ('''<span style="text-decoration: ''', 
                'underline;"></span>'), 
                no_outer_pgraphs = True )],# underlined
['section'      ,tp(add_outside = ('<h1><b>','</b></h1>'),
    call_first = [section_num])],
['section\*'    ,tp(add_outside = ('<h1><b>','</b></h1>'),)],
['subsection'   ,tp(add_outside = ('<h2><b>','</b></h2>'),
    call_first = [subsection_num])], 
['subsection*' ,tp(add_outside = ('<h2><b>','</b></h2>'))], 
]
txt_attr_dict = build_dict('txt_attr', txt_attributes, 
                           r'\\{0}\{{', r'\{{', r'\}}')

other_attributes = [
# TODO: why do I have to add a space for the first character of add_outside???
# They must be being consumed somewhere
['href'     ,tp(add_outside = (' <a href="{0}">', '</a>'),
                no_outer_pgraphs=True,
                call_first = href_call)]
]
other_attr_dict = build_dict('other_attr', other_attributes,
                              r'\\{0}\{{.*?}}\{{', None,r'\}}')

#################
## Custom items - #TODO NOT YET TESTED
# if you REALLY need to do your own custom regular expression matching,
# you can do so here. NOTE that you do NOT need to put parenthesis around
# the pattern, as this will be done automatically.
custom_items = [
#[['regexp insisde'], ['regexp outside'], ['regexp end']], tp()]
]

custom_dict = build_dict('custom', custom_items)
                         
###########################
## Create some final formatting substitutions
## These should generally be of very few characters.

from cloudtb.extra import richtext
final_subs = [
[r'\#'      ,'#'],
[r'\$'      ,"$"],
[r'\%'      ,"%"],
[r'{*}'     ,r'* '],
[r'{[}'     ,r'['],
[r'{]}'     ,r']'],
[r'\{'      ,r'{'],
[r'\}'      ,r'}'],
[r'<'       ,r'&lt;'],
[r'>'       ,r'&gt;'],
[r'\&'      ,r'&amp;'],
[r'"'       ,r'&quot;'],
[r'\textbackslash{}'    ,'\\'],
[r'\textasciitilde{}'   ,r'~'],
[r'\textasciicircum{}'  ,r'^'],
[r'\textendash{}'       ,r'-']
#    [r''    ,r''],
]
final_subs = [(textools.convert_to_regexp(n[0], compile = True), n[1])
               for n in final_subs]

##### SUMMARY
# So, the objects we have are:
# Dictionaries, which were created to automaticaly format reg expressions
# begin_dict    - contains \begin \end statements
# if_dict       - \if \endif statements
# txt_attr_dict - text attributes of form \attr{modified text}
# line_dict     - variables of a single line, i.e. \header MY HEADER\n
#
# We also have final_subs, which substitutes characters in so wordpress can
#   read them.

def concatenate_dicts(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out

every_dict_formatting = concatenate_dicts(begin_dict, if_dict, txt_attr_dict,
                          other_attr_dict, custom_dict)

if __name__ == '__main__':
    import wordtex
    from cloudtb import dbe
    wordtex.main()
    