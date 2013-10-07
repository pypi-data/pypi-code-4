# -*- coding: utf-8 -*-



class Declaration:
    '''
    Describes one graph or template declaration.
    
    Available attributes:
        template template-name
        
        input NAME FRRDFILE DS CF
        input-file NAME RRDFILE
        input-dir NAME PATH 
        input-ds NAME DS
        input-cf NAME CF

        output-dir PATH
        output-file FILE
        output-prefix PREFIX
        output-suffix SUFFIX
        output-format FORMAT
        # output file: OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT

        option option-name option-value
        option ...
        ...

        size SIZE [SIZE, ...]

        line (with EXPR | use NAME) [color COLOR] [text LEGEND] [stack]
        area -||-

        gprint text TEXT with EXPR get AGGR 
        comment text TEXT
        


    Declarations:
        Template TEMPLATE_NAME 
        Graph GRAPH_NAME    
    '''
    
    
    UNKNOWN, TEMPLATE, GRAPH = -1, 0, 1
    
    
    def __init__(self):
        self.inputs = {}
        self.output = {
            'dir': '',
            'prefix': '',
            'suffix': '',
            'format': 'png'
            }
        self.sizes = []
        self.options = {}
        self.decls = []
        
        self.decl_class = Declaration.UNKNOWN


    def set_template(self):
        '''
        makes this declaration a template
        '''
        self.decl_class = Declaration.TEMPLATE


    def set_graph(self):
        '''
        makes this declaration a graph
        '''
        self.decl_class = Declaration.GRAPH


    def is_graph(self):
        return self.decl_class == Declaration.GRAPH


    def use(self, decl):
        '''
        Load all values from other declaration.
        NOTE: this could overwrite existing values!
        TODO: we may want to preserve values
        '''
        self.inputs = decl.inputs.copy()
        self.output = decl.output.copy()
        self.sizes = [a for a in decl.sizes]
        self.options = decl.options.copy()
        self.decls = [a for a in decl.decls]
        


    def add_input(self, name, file_, ds=None, cf=None):
        '''
        Adds one-line input with given name.
        Inserting input which already exists is an error.
        TODO: guessing ds and cf (when not given) based 
        on reading file
        '''
        
        from os import path
        
        if name in self.inputs:
            raise ValueError('Input "%s" already exists' % name)

        self.inputs[name] = {
            'dir': path.dirname(file_),
            'file': path.basename(file_),
            'ds': ds,
            'cf': cf
            }
    
    
    def input_file(self, name, file_):
        '''
        Set file for input named 'name'.
        If input doesn't exists - it would be created.
        If input exists already - it's file (and maybe dir) values will
        be overwritten. 
        file_ may be filename or file path (in that case the 'dir' value
        will be also set.
        '''
        from os import path
        
        d, f = path.split(file_)
        if name not in self.inputs:
            self.inputs[name] = {}
        
        self.inputs[name]['file'] = f
        if d:
            self.inputs[name]['dir'] = d
            
            
    def input_dir(self, name, dir_=None):
        '''
        Set dir value for input named 'name'.
        If specified input doesn't exists it would be created.
        
        if dir is not specified, then:
         - name is treated as dir
         - dir is set for each known input
        '''
        
        # for clarifying
        if dir_ is None:
            dir_ = name
            name = None
        
        
        if not name:
            for v in self.inputs.values():
                v['dir'] = dir_
        else:
            if name not in self.inputs:
                self.inputs[name] = {}    
            self.inputs[name]['dir'] = dir_


    def input_ds(self, name, ds):
        '''
        Set ds value for input named 'name'.
        If specified input doesn't exists it would be created.
        '''
        
        if name not in self.inputs:
            self.inputs[name] = {}
            
        self.inputs[name]['ds'] = ds


    def input_cf(self, name, cf):
        '''
        Set cf value for input named 'name'.
        If specified input doesn't exists it would be created.
        '''
        
        if name not in self.inputs:
            self.inputs[name] = {}
            
        self.inputs[name]['cf'] = cf


    def output_dir(self, path):
        '''
        Sets an output destination directory
        '''
        
        self.output['dir'] = path


    def output_file(self, file_):
        '''
        Sets an output dir, prefix, suffix and format based on 
        filename. 
        TODO: there should be way to feed this method that it would
        parse filename for sizes and other templates. Currently we're only 
        setting prefix as filename - which is bit tricky.
        '''
        
        from os import path
        
        d, f = path.split(file_)
        if d:
            self.output['dir'] = d
            
        f, e = path.splitext(f)
        self.output['prefix'] = f
        #self.output['suffix'] = '' we may want to uncomment that
        self.output['format'] = e[1:]
        
        
    def output_prefix(self, prefix):
        '''
        Sets filename prefix to be used.
        Output filepath will be created as:
            OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT
        '''
        
        self.output['prefix'] = prefix


    def output_suffix(self, suffix):
        '''
        Sets filename suffix to be used.
        Output filepath will be created as:
            OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT
        '''
        
        self.output['suffix'] = suffix
        
        
    def output_format(self, format_):
         '''
         set output file format
         '''
         self.output['format'] = format_
         
         
    def add_size(self, size):
        '''
        adds graph dimensions, in which we want graph to be generated
        size should be one of:
         - str in form: 'WxH' - w-width, h-height, x-x :)
         - tuple with two int, example: (160, 120)
        '''
        
        if type(size) in (tuple, list):
            self.sizes.append(tuple(size))
        elif type(size) == str:
            w, h = size.split('x')
            w, h = int(w), int(h)
            self.sizes.append((w,h))
        else:
            raise ValueError('Size format (%s) is not supported' % str(type(size)))


    def add_dec(self, decl_name, expr=None, name=None, aggr=None, color=None, text=None, stack=None):
        '''
        adds complex declaration, for lines, areas and so forth
        TODO: update this method so it won't add unneeded or unset data
        '''
        if expr and name:
            raise ValueError('There should be only expr or value defined, not both!')

        decl = (decl_name, {
                'expr': expr,
                'name': name,
                'aggr': aggr,
                'color': color,
                'text': text,
                'stack': stack,
            })
        self.decls.append(decl)


    def add_line1(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line1', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_line2(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line2', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_line3(self, expr=None, name=None, color=None, text=None, stack=None):
        self.add_dec('line3', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_area(self, expr=None, name=None, color=None, text=None, stack=None):
        
        self.add_dec('area', expr=expr, name=name, color=color, text=text, stack=stack)

    def add_gprint(self, expr=None, name=None, aggr=None, text=None):
        self.add_dec('gprint', expr=expr, name=name, aggr=aggr, text=text)

    def add_comment(self, text=None):
        self.add_dec('comment', text=text)

    
    def add_option(self, option_name, value):
        
        # we need to hack rrd graph a bit, because we need to know
        # the datatype of the param
        from rrd.graph import Graph
        opname = option_name.replace('-', '_')
        datatype = Graph.SIMPLE_KEYWORDS[opname][0]
        
        self.options[opname] = datatype(value)
    
    
    def _random_name(self):
        import random
        s = ''
        c = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for _ in range(10):
            s += c[random.randrange(len(c))]
        return s
        
    
    def _call_by_type(self, g, t, vname, decl):
        if t in ('line1', 'line2', 'line3', 'area'):
            getattr(g, t)(vname, decl['color'], decl['text'], decl['stack'])
        elif t in ('gprint',):
            getattr(g, t)(vname, decl['text'])
            


    def get_graph(self):
        '''
        Prepares an Graph instance(s) based on passed data.
        This method will return as many graphs as many size declaration
        was passed.
        '''
        
        if self.decl_class != Declaration.GRAPH:
            raise AttributeError('Only graph declaration may be graphed')
        
        from rrd.graph import Graph
        import os        

        ret = []
        for s in self.sizes:
            g = Graph()
            g.width(s[0])
            g.height(s[1])
            
            for optname, optval in self.options.items():
                getattr(g, optname)(optval)
            
            g.filename(os.path.join(
                self.output['dir'],
                self.output['prefix'] + '%ix%i' % s + self.output['suffix'] + '.' + self.output['format']
            ))
            
            for vname, inp in self.inputs.items():
                g.def_(vname, os.path.join(inp['dir'], inp['file']), inp['ds'], inp['cf'])
            
            for t, decl in self.decls:
                if t in ('comment'):
                    g.comment(decl['text'])
                    continue
                    
                if decl['aggr']:
                    rndname = self._random_name()
                    if decl['name']:
                        w = decl['name']
                    elif decl['expr']:
                        w = self._random_name()
                        g.cdef(w, decl['expr'])
                    g.vdef(rndname, w, decl['aggr'])
                    self._call_by_type(g, t, rndname, decl)
                    #getattr(g, t)(rndname, decl['color'], decl['text'], decl['stack'])
                else:
                    if decl['name']:
                        self._call_by_type(g, t, decl['name'], decl)
                        #getattr(g, t)(decl['name'], decl['color'], decl['text'], decl['stack'])
                    elif decl['expr']:
                        rndname = self._random_name()
                        g.cdef(rndname, decl['expr'])
                        self._call_by_type(g, t, rndname, decl)
                        #getattr(g, t)(rndname, decl['color'], decl['text'], decl['stack'])


            
            ret.append(g)
            
        return tuple(ret)
