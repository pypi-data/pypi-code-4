#!/usr/bin/python
# -*- coding: utf-8 -*-
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2.1
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

import pdb
import re
import copy
from cloudtb import textools, iteration

watched = []

class LatexError(ValueError):
    def __init__(self, msg = '', line = '?'):
        ValueError.__init__(self)
        self.line = line
        self.msg = msg
        
    def __str__(self):
        msg = ("LaTeX LaTeX Error at line "
            "{0}: ").format(self.line) + repr(self.msg)
        return msg

def format_paragraph(text_data):
    pass

def format_font(text_data):
    pass

def format_outside(text_data, add_outside):
    pass

###################################3
## GENERAL FUNCTIONS   

def get_text_data(text_objects, texpart_constructor, return_first = False):
    '''
    This is the primary function for converting data into TexParts.
    Inputs:
        text_objects - list of strings and TexParts, must have been formated by
            reform_text
        texpart_constructor - the constructor used, normally defined in
            a list in wp_formatting.py
        return_first - only used by the get_document function, returns only
            the first object found.
    Output:
        returns the fully created text_data that is held in all TexPart objects
        
    The internal workings are as follows:    
    given the matches, creates it in a readable array
    (2, txt3),  # value was the first inside start of group    
    (True, txt1),
    (True, txt2),
    (True, TxtPart),
    (3, txt4),  # text was the final end of group
    (False, txt2),
    (False, TxtPart),
    etc...
    
    where True means that the text is inside your match parameters and False
    means they are outside. 2 and 3 are documented above.
    
    Note, the inside list takes precedence over the starter list, and the starter
    list takes precedence over the end list.
    This means that if something matches inside it will not match starter, etc.
    It is best to make your "insides" specific and not use special re 
    characters like .* etc.
    
    If a starters is imbeded in an inside, it is considered inside. For instance
    /iffase /ifblog no hello to world /fi /fi -- ifblog will be inside of /iffalse
    '''
    inside_list, starters_list, end_list = texpart_constructor.match_re
    re_in = textools.re_in
    
    # error checking on file
    match_cmp = re.compile('|'.join(inside_list + starters_list + end_list))
    
    # split up text for compiling
    splited = []
    for tobj in text_objects:
        if type(tobj) != str:
            splited.append(tobj)
        else:
            researched = textools.re_search(match_cmp, tobj)
            splited.extend(textools.get_iter_str_researched(researched))
        
    inside = [re.compile(m) for m in inside_list]
    starter = [re.compile(m) for m in starters_list]
    end = [re.compile(m) for m in end_list]
    
    num_in = 0
    set_num = None
    inout = []
    #TODO: It has to match arbitrary if statements. I think this should be
    # pretty easy
    for txt in splited:
#        if type(txt) == str and 'Garrett' in txt and 'section' in texpart_constructor.label:
#            print texpart_constructor.label
#            pdb.set_trace()
        assert(num_in >= 0)
        if txt in (None, ''):
            continue
        elif type(txt) == TexPart:
            pass    # TexParts have been alrady processed.
        elif re_in(txt, inside):
            if num_in == 0:
                set_num = 2
            num_in += 1
        elif num_in > 0 and re_in(txt, starter):
            # i.e. if you wrote something like /iffalse /ifblog
            num_in += 1
        elif num_in > 0 and re_in(txt, end):
            # make sure we only count ends if you are removing!
            num_in -= 1
            if num_in == 0:
                set_num = 3
        
        if set_num:
            inout.append((set_num, txt))
            set_num = None
        elif num_in > 0:
            inout.append((True, txt))
        else:
            inout.append((False, txt))
    
    return convert_inout(inout, texpart_constructor, 
                         return_first=return_first)

def reform_text(text_data, is_in = False, no_indicators = False):
    '''put all text objects that are next to eachother into a 
    single string
    is_in = None ignores the values. No_indicators means they don't exist
    (single dimension list)'''
    all_txt = []
    out = []
    if no_indicators:
        is_in = None
    
    for item in text_data:
        if no_indicators:
            txt = item
        else:
            n, txt = item
        
        if is_in == None:
            pass
        elif is_in == False:
            assert(n == 0)  # something wasn't processed!
        else:
            assert(n > 0)
        if type(txt) != str:
            if all_txt:
                out.append(''.join(all_txt))
                all_txt = []
            out.append(txt)
        else:
            all_txt.append(txt)
    if all_txt:
        out.append(''.join(all_txt))
    return out

def process_document(path):
    '''converts the document into a list of recursively generated TextParts
    Each of which has an object called text_data that stores the strings and
    other TextParts that comprise it.
    '''
    with open(path) as f:
        text = f.read()

    # Get the document part
    document_type = TexPart.FORMAT_MODULE.begin_dict['document']
    document = get_text_data([text], document_type, return_first = True)
    return document

def print_tex_tree(texpart, tabs = 0):
    tform = ' '*(2*tabs) + '- {0}'
    if type(texpart) == str:
        print tform.format('base string len: ' + str(len(texpart)))
    else:
        print tform.format(texpart.label),
        print  ' ||start:{0} |end:{1}'.format(repr(texpart.start_txt), 
                                              repr(texpart.end_txt))
        tabs += 1
        for tp in texpart.text_data:
            print_tex_tree(tp, tabs)

def convert_inout(inout, texpart_constructor, return_first = False):
    if len(inout) == 1:
        assert(inout[0][0] == False)
        return [inout[0][1]]
    
    def convert_processed(start, body, end):
#        if 'tabular' in texpart_constructor.label:
#            pdb.set_trace()
        assert(start[0] == 2 and end[0] == 3)
        body = reform_text(body, is_in = True)
        tp = copy.copy( texpart_constructor)
        tp.init_text((start[1], body, end[1]))
        print 'Converting', start
        return tp
    
    def get_processed(was_in, processing):
        if was_in > 0:  # object
            assert(processing[0][0] == 2 and processing[-1][0] == 3)
            converted = convert_processed(processing[0],
                    processing[1:-1], processing[-1])
            return [converted]
        else:
            return reform_text(processing)
    
    text = []
    prev_indicator = None
    process = False
    processing = []
    next_processing = []
    # goes through text list and organizes things by whether they are
    # in or out. Then converts them to the specified constructor
    for i, item in enumerate(inout):
        indicator, ti = item
        
        if prev_indicator == None:
            prev_indicator = indicator
        
        if indicator == 2 and prev_indicator == 0:
            process = True
            # no append, keep current item for next round
            next_processing = [item]
        elif indicator == 2 and prev_indicator != 2:    # should only happen at beginning
            assert(prev_indicator == 3)
            assert(not processing)
            process = False
            processing.append(item)
        elif indicator == 3:
            assert(prev_indicator in (1,2))
            process = True
            processing.append(item)
            next_processing = []
        else:
            process = False
            processing.append(item)
            
        if process:
            data = get_processed(prev_indicator, processing)
            text.extend(data)
            processing = next_processing
            if prev_indicator and return_first:
                return data[0]
        prev_indicator = indicator
    
    if processing:
        data = get_processed(prev_indicator, processing)
        text.extend(data)
        if prev_indicator and return_first:
            return data[0]
    
    assert(type(text) == list)
    return text

class TexPart(object):
    '''This is the primary object of this library. It does most of the
    processing work, and is what the entire document get's turned into.
    See wp_formatting for information on how to extend the module using these --
    hopefully you'll find it pretty simple!
    '''
    # It would be extremely easy to make this module export, say, true html.
    # all one would have to do is copy - paste the wp_formatting file and
    # put in the proper values. Then change the below module globally
    # (texlib.TexPart.FORMAT_MODULE = new_format_module).
    # It would only require the change of a few lines of code otherwise...
    # I think!
    FORMAT_MODULE = None
    
    def __init__(self, 
                 label = None, 
                 no_update_text = None, 
                 format_call = None,
                 call_first = None, 
                 call_last = None,
                 no_std_format = None, 
                 no_one_spaces = None,
                 no_paragraphs = False, 
                 add_outside = None, 
                 no_outer_pgraphs = None,
                 no_final_subs = None,):
        '''
        label - used for debuging and to construct tree view
        
        no_update_text - update_text will not be called on this module once
            it is discovered (it cannot contain ANY internal TexPart objects)
            Will still call wp_formatting options. Recommended to set
            no_std_formating = True and other desired attributes
        
        # useful for very custom types
        call_first - call this list of functions before any formating
        call_last - call this list of functions after all formating
        
        # no_std_format disables all these
        no_std_format = std_format won't be called during format. Will
            still be called on internal data.
        no_paragraphs - override std format and don't use paragraphs for next
            lines. Will still have outer paragraphs unless overriden
        no_one_spaces - overrides std format to reduce all spaces to one.
        
        # Extra. Not affected by above (except call last of course)
        add_outside - this is the outside characters that will be added
            during the format call (front, back). Note: processed before
            outer_pgraphs (paragraphs go outside of front/back).
        no_outer_pgraphs - makes it so the object does not have paragraphs
            around it.
        no_final_subs - final substitutions (i.e. \$ -> $) won't be made.
            will still be called on internal data
        '''
        self.label = label      # convinience, mostly for debugging
        
        self.no_update_text = no_update_text
        
        if call_first != None and not hasattr(call_first, '__iter__'):
            call_first = (call_first,)
        if call_last != None and not hasattr(call_last, '__iter__'):
            call_last = (call_last,)
        self.call_first = call_first
        self.call_last = call_last
        
        self.no_std_format = no_std_format
        self.no_one_spaces = no_one_spaces
        self.no_paragraphs = no_paragraphs
        
        self.add_outside = add_outside
        self.no_outer_pgraphs = no_outer_pgraphs
        self.no_final_subs = no_final_subs
 
        self.match_re = None
        self._init_text_block = None
        self.is_origional_text = None
        self.is_done = False
    
    def update_match_re(self, match_re):
        match_re = [[textools.ensure_parenthesis(n) for n in m] for m in match_re]
        self.match_re = match_re
        self.cmp_inside, self.cmp_starters, self.cmp_end = (
            [[re.compile(n) for n in c] for c in self.match_re])
        
    def init_text(self, text_block, use_dict = None):
        '''
        This function initilizes the text data and calls update_text       
        '''
        self.start_txt, self.text_data, self.end_txt = text_block
        assert(type(self.text_data) == list)
        self._init_text_block = self.start_txt, self.text_data[:], self.end_txt
        global watched
        watched.append((self.label, self))
        self.update_text(use_dict=use_dict)
        
    def get_original_text(self, no_start_stop = False):
        '''Returns the original format of the string, recursively going to all
        it's children until everything is back to a single string form.
        
        Must be called before format or get_wp_text is called.
        '''
        if self.is_origional_text:
            body, = self.text_data
            assert(type(body) == str)
            if no_start_stop:
                return body
            else:
                return self.start_txt + body + self.end_txt
        if self.is_done:
            raise Exception("cannot undo formating: already called format")
        text_data = self.text_data[:]
        for i, td in enumerate(text_data):
            if type(td) != str:
                text_data[i] = td.get_original_text()
        body = ''.join(text_data)
        if no_start_stop:
            return body
        return self.start_txt + body + self.end_txt
    
    def reset_text(self):
        self.text_data = [self.get_original_text(no_start_stop = True)]
        self.is_origional_text = True
    
    def check_no_update_text(self):
        '''performs a check that converts all objects that didn't want their
        text to be modified into their original form.'''
        if self.no_update_text:
            self.reset_text()
            return
        for td in self.text_data:
            if type(td) == str:
                pass
            elif td.no_update_text:
                td.reset_text()
            else:
                td.check_no_update_text()
    
    def update_text(self, use_dict = None):
        '''Turns the text body into a set of str objects and TexPart objects
        Updates recursively'''
        if self.no_update_text:
            self.reset_text()
            return
        self.is_origional_text = False
        if use_dict == None:
            use_dict = self.FORMAT_MODULE.every_dict_formatting
        assert(type(self.text_data) == list)
        if not self.text_data:
            return
        for key, texpart in use_dict.iteritems():
#            if self.label == 'tabrow function: tabular_call' and key == 'false':
#                pdb.set_trace()
            self.text_data = get_text_data(self.text_data, texpart)
            assert(type(self.text_data) == list)
            assert(self.text_data)
                
    def insert_tex(self, index, data):
        return self.text_data.insert(index, data)
    
    def append_tex(self, data):
        return self.text_data.append(data)
    
    def get_wp_text(self):
        self.format()
        wptext = []
        for tp in self.text_data:
            if type(tp) == str:
                wptext.append(tp)
            else:
                wptext.append(tp.get_wp_text())
        return ''.join(wptext)
    
    def format(self):
        if self.is_done:
            return
        self.check_no_update_text()
        self.is_done = True
        
        if self.call_first: 
            [cf(self) for cf in self.call_first]
        
        if self.no_std_format:
            self.no_paragraphs = self.no_one_spaces = True
            
        self.std_format()
        
        if self.add_outside:
            self.insert_tex(0, self.add_outside[0])
            self.append_tex(self.add_outside[1])
            
        if not self.no_outer_pgraphs:
            self.insert_tex(0, self.FORMAT_MODULE.PARAGRAPH[0])
            self.append_tex(self.FORMAT_MODULE.PARAGRAPH[1])

        if self.call_last: 
            [cl(self) for cl in self.call_last]
        
        if not self.no_update_text:
            for tp in self.text_data:
                if type(tp) != str:
                    tp.format()
    
    def special_format(self, format_subs):
        '''convinience function for external functions to call with their own
        wp_formatting substitutions. See wp_formatting.final_subs for an example
        The input format_subs MUST be in regexp form!
        Best to call during a "call_last" function call.
        Note: this automatically strips newlines and spaces from front and
        back of elements
        '''
        for i, tp in enumerate(self.text_data):
            if type(tp) != str:
                continue
            tp = tp.strip()
            self.text_data[i] = textools.replace_text_with_list(format_subs, tp)
        
    def std_format(self):
        ''' performs standard formating.
        Currently:
            - converts double line spaces to paragraph boundaries.
                - Note: if std_format is set then paragraph boundaries
                    are automatically added to the outside of the item.
                    To disable all paragraph boundaries, use 
            - makes sure all spaces are only single spaces
            - goes through the final subs and converts them
        '''
        if self.label == 'tabular_column_custom dict:tabular_call':
            pdb.set_trace
        fmat = self.FORMAT_MODULE
        one_space = (' {2,}', ' ')
        paragraphs = ('\n{2,}', ''.join(fmat.PARAGRAPH))
        all_subs = []
        if not self.no_final_subs:
            all_subs += fmat.final_subs
        if not self.no_paragraphs:
            all_subs += [paragraphs]
        if not self.no_one_spaces:
            all_subs += [one_space]
        
        # get the functions for matching and replacing
        all_subs_or_re, all_subs_re_replace = textools.get_rcmp_list(all_subs)
        
        # create the subfunction for replacement
        subfun = textools.subfun(replace_list = all_subs_re_replace)
        for i, tp in enumerate(self.text_data):
            if type(tp) != str:
                continue
            # strip all dangling new-lines and spaces
            tp = all_subs_or_re.sub(subfun, tp)
            tp = re.sub('\n', ' ', tp)
            if not self.no_std_format:
                tp = tp.strip()
            self.text_data[i] = tp
            
        
    def __repr__(self):
        return 'TPart(' + str(self.label) + ')'
    
    def __str__(self):
        return self.label

if __name__ == '__main__':
    import wordtex
    from cloudtb import dbe
    wordtex.main()