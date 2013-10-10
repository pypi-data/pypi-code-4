# -*- coding: utf-8 -*-

from pyparsing import Dict, Group, Word, QuotedString, Keyword, White, LineEnd, LineStart, Regex, OnlyOnce, OneOrMore, Optional, alphanums, alphas, printables, restOfLine, oneOf
import pyparsing
import logging


def create_grammar():
    names = alphanums + '._-'
    
    decl = Group((Keyword('graph', caseless=True) | Keyword('template', caseless=True)) + Word(names) + LineEnd())
    include = Group(Keyword('include', caseless=True) + Word(printables) + LineEnd())
    eq = Optional(Word('='), default='=')
    
    String = QuotedString('"') | Word(printables)
    Names = Word(names)
    
    
    
    
    cmds = White(' \t') + \
        (
            (
                Keyword('use', caseless=True) + Names
            ) | (
                Keyword('input', caseless=True) 
                + OneOrMore(
                        (Keyword('name') + eq + Names)
                        |
                        (Keyword('file') + eq + String)
                        |
                        (Keyword('dir') + eq  + String)
                        |
                        (Keyword('ds') + eq + Names)
                        |
                        (Keyword('cf') + eq + Names)
                    )
            ) | (
                Keyword('output', caseless=True)
                + OneOrMore(
                        (Keyword('dir') + eq + String)
                        |
                        (Keyword('file') + eq + String)
                        |
                        (Keyword('prefix') + eq + Names)
                        |
                        (Keyword('suffix') + eq + Names)
                        |
                        (Keyword('format') + eq + Names)
                    )
            ) | (
                Keyword('size', caseless=True) + OneOrMore(Regex('[0-9]+x[0-9]+'))
            ) | (
                Keyword('option', caseless=True) + Names + eq + String
            ) | (
                
                (
                    Keyword('line1', caseless=True) | 
                    Keyword('line2', caseless=True) | 
                    Keyword('line3', caseless=True) | 
                    Keyword('area', caseless=True) |
                    Keyword('comment', caseless=True)
                ) + OneOrMore(
                    ((Keyword('with', caseless=True) + eq + Word(printables) | Keyword('use', caseless=True) + eq + Word(alphanums))) |
                    (Keyword('color', caseless=True) + eq + Word(alphanums)) |
                    (Keyword('text', caseless=True) + eq + String) |
                    (Keyword('stack', caseless=True))
                )
            ) | (
                Keyword('gprint', caseless=True) + OneOrMore(
                    (Keyword('use', caseless=True) + eq + Word(names)) |
                    (Keyword('get', caseless=True) + eq + Word(names)) |
                    (Keyword('with', caseless=True) + eq + Word(printables)) |
                    (Keyword('text', caseless=True) + eq + String)
                )
            ) | (
                Keyword('comment', caseless=True)
                + (Keyword('text', caseless=True) + eq + String)
            )
        ) + LineEnd()
    
    
    
    grammar = Group((decl) + OneOrMore(Group(cmds)) | include)    
    grammar.ignore(
        Word('#') + restOfLine
        )
    
    return Group(grammar)


def _parse_config(cfg):
    '''
    Parses configuration
    '''
    grammar = OneOrMore( create_grammar() )
    return grammar.parseString(cfg, parseAll=True)




def _extr_params(cmd, params):
    '''
    extracts parameters from cmd list and places them in 
    params dict
    '''
    it = iter(cmd)
    try:
        while True:
            c = it.next()
            if c not in ('stack',):
                it.next() # skip eq
                v = it.next()
            else:
                v = 'STACK'
            params[c] = v
    except StopIteration:
        pass
    
    return params



def _parse_cmd(decl, cmd):
    '''
    parses command from cmd list and updates
    its corresponding value in decl class
    '''
    
    # we have to handle them in special manner
    # line1, line2, line3, area, gprint
    
    if cmd[0] in ('area', 'line1', 'line2', 'line3'):
        params = {'with':None, 'use':None, 'color':None, 'text':None, 'stack':None}
        _extr_params(cmd[1:], params)       

        getattr(decl, 'add_%s' % cmd[0])(
                name=params['use'],
                expr=params['with'],
                color=params['color'],
                text=params['text'],
                stack=params['stack']
            )
        return
    
    if cmd[0] == 'gprint':
        params = {'with':None, 'get':None, 'use':None, 'text':None}
        _extr_params(cmd[1:], params)
        
        getattr(decl, 'add_gprint')(
            name=params['use'],
            expr=params['with'],
            aggr=params['get'],
            text=params['text'],
            )
        
        return
    
    if cmd[0] == 'comment':
        params = {'text':None}
        _extr_params(cmd[1:], params)
        
        getattr(decl, 'add_comment')(
            text=params['text']
            )
        return 
    
    if cmd[0] == 'input':
        params = {}
        _extr_params(cmd[1:], params)
        try:
            name = params['name']
        except KeyError:
            name = None
        
        for k, v in params.items():
            if k == 'name':
                continue
            
            method = 'input_%s' % k
            getattr(decl, method)(v, name=name)
        return
        
    if cmd[0] == 'output':
        params = {}
        _extr_params(cmd[1:], params)

        for k, v in params.items():
            method = 'output_%s' % k
            getattr(decl, method)(v)
        return
        
    params = {}
    _extr_params(cmd[1:], params)
    
    method = cmd[0].replace('-', '_')
    if method in ('option'):
        for k, v in params.items():
            method = 'add_%s' % (method)
            getattr(decl, method)(k, v)
    if method in ('size'):
        for v in cmd[1:]:
            getattr(decl, 'add_size')(v)
            
    #getattr(decl, method)(*cmd[1:])
    


def print_parse_error(pe, cnt, filename=None):
    '''
    Prints nice parse error information
    pe - pyparsing.ParseException
    cnt - parsed contents 
    filename - ;)
    '''
    logging.error('Error parsing configuration from %s at line %i' % (str(filename), pe.lineno))       
    logging.warn(str(pe))
    
    from math import ceil, log10
    
    lines = cnt.splitlines()
    nums = int(ceil(log10(len(lines)+1)))
    fmt = '%0'+str(nums)+'i: %s'

    for i in range(max(pe.lineno-4, 0), pe.lineno):
        logging.info(fmt % (i+1, lines[i]))
    logging.info(' '*(2+nums)+'^'*len(lines[pe.lineno-1]))
    for i in range(pe.lineno, min(pe.lineno+4, len(lines))):
        logging.info(fmt % (i+1, lines[i]))    



def parse(cnt, OPTIONS, decls={}):
    '''
    Parses configuration given as str
    '''
    from declaration import Declaration
    
    for r in _parse_config(cnt):
        cmddef, cmdname = r[0][0][:2]

        if cmddef == 'include':
            logging.debug('Including file %s' % cmdname)
            decls.update(load_config(cmdname, OPTIONS, decls))
        elif cmddef in ('graph', 'template'):
            decl = Declaration()
            if cmddef == 'graph':
                decl.set_graph()
            elif cmddef == 'template':
                decl.set_template()
            
            for c in r[0][1:]:
                c = c[1:-1] # first element is an identation, last is newline
                
                if c[0] == 'use':
                    try:
                        logging.debug('Declaration %s will use %s' % (cmdname, c[1]))
                        decl.use(decls[c[1]])
                    except KeyError:
                        logging.error('There is no such template: "%s" (in declaration: %s)' % (c[1], cmdname))
                        logging.debug('Templates available from here:')
                        for k, d in decls.items():
                            logging.debug('\t' + str(k))
                        
                else:
                    _parse_cmd(decl, c)
            
            decls[cmdname] = decl
            

    return decls



def load_config(path, OPTIONS, decls={}):
    '''
    Load configuration from file.
    Path may be str (meaning single file) 
    or list of pathes.
    '''
    
    if type(path) is list:
        for f in path:
            decls.update(load_config(f, OPTIONS, decls))
        return decls
    
    import os
    for cp in OPTIONS['conf-dir']:
        p = os.path.join(cp, path)
        if os.path.exists(p) and os.path.isfile(p):
            path = p
            break
    
    logging.debug('Parsing file %s' % path)
    fcnt = open(path).read()
    try:
        decl = parse(fcnt, OPTIONS, decls)
        decls.update(decl)
    except pyparsing.ParseException as pe:
        print_parse_error(pe, fcnt, path)
    
    
    return decls
    
