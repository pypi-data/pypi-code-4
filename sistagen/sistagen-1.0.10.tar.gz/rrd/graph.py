# -*- coding: utf-8 -*-

class Graph(object):
    '''
    Wrapper for rrd graph.
    This class accepts all rrd graph parameters.
    All parameters should be passed into Graph object 
    by just calling method with parameter name and its value as argument,
    for example: graph.width(240) - will set graph width to 240 px
    Data and graph definitions are set in same manner, the only difference 
    is that there are several method arguments, for example:
    graph.line1('data', 'ff0000', 'Simple data')
    NOTE:
    As the 'def' is keyword in python, and RRDTool uses it, we need to 
    call def_ instead.
    
    Example:
    import rrd
    graph = rrd.Graph()
    graph.width(640)
    graph.height(480)
    graph.filename('test.png')
    graph.def_('idle', 'cpu-idle.rrd', 'value', 'AVERAGE')
    graph.def_('system', '/tmp/cpu-0/cpu-system.rrd', 'value', 'AVERAGE')
    graph.def_('user', '/tmp/cpu-0/cpu-user.rrd', 'value', 'AVERAGE')
    graph.area('idle', '00ff0050', '', 'STACK')
    graph.area('system', 'ff000050', '', 'STACK')
    graph.area('user', '0000ff50', '', 'STACK')
    graph.graph()
    
    
    There is also possibility to run all of those inline.
    Pythons' dicts are unordered, and rrdtool needs data to be fed
    in specified order, so we have to push the data in form of list of tuples,
    instead of simple dict or **kwargs. 
    It could get quite complex sometimes, but may be useful.
    
    In its general form, initializator gets data in form of list of tuples:
    [ ('data_name': value), ...]
    where data_name is name of the parameter and value may be:
        simple value (such as width, height, etc)
        complex value (def_, cdef, line1, etc)
    in both cases, value should be left in form, as it would be passed into function.
     
    
    Example:
    Graph(
        [('width',240), ('height',160), ('filename','test.png'), 
            ('def_', ('idle', 'cpu-idle.rrd', 'value', 'AVERAGE')), 
            ('area', ('idle', '00ff0050', '', 'STACK'))
        ]).graph()
    '''
    
    SIMPLE_KEYWORDS = {
        'filename': (str, None),
        'start': (int, '--'), 's': (int, '-'),
        'end': (int, '--'), 'e': (int, '-'),
        'width': (int, '--'), 'w': (int, '-'),
        'height': (int, '--'), 'h': (int, '-'),
        'x_grid': (int, '--'), 'x': (int, '-'),
        'y_grid': (int, '--'), 'y': (int, '-'),
        'units-exponent': (str, '--'), 
        'vertical-label': (str, '--'), 'v': (str, '-'),
        'imginfo': (str, '--'), 'f': (str, '-'),
        'imgformat': (str, '--'), 'a': (str, '-'),
        'background': (str, '--'), 'B': (str, '-'),
        'overlay': (str, '--'), 'O': (str, '-'),
        'unit': (str, '--'), 'U': (str, '-'),
        'upper_limit': (int, '--'), 'u': (int, '-'),
        'lower_limit': (int, '--'), 'l': (int, '-'),
        'step': (int, '--'),
        'base': (int, '--'), 'b': (int, '-'),
        'color': (str, '--'), 'c': (str, '-'),
        'title': (str, '--'), 't': (str, '-'),
        
        'interlaced': (bool, '--'), 'i': (bool, '-'),
        'lazy': (bool, '--'), 'z': (bool, '-'),
        'logarithmic': (bool, '--'), 'o': (bool, '-'),
        'no_legend': (bool, '--'), 'g': (bool, '-'),
        'rigid': (bool, '--'), 'r': (bool, '-'),
        'alt_y_grid': (bool, '--'), 
        'alt_y_mrtg': (bool, '--'), 
        'alt_autoscale': (bool, '--'), 
        'alt_autoscale_max': (bool, '--'), 
        }
    
    MULTI_KEYWORDS = {
        'def_': ([('vname', True), ('rrd', True), ('ds', True), ('cf', True)], 'DEF:%(vname)s=%(rrd)s:%(ds)s:%(cf)s'),
        'cdef': ([('vname', True), ('rpn', True)], 'CDEF:%(vname)s=%(rpn)s'),
        'vdef': ([('vname', True), ('aggrfld', True), ('aggrfnc', True)], 'VDEF:%(vname)s=%(aggrfld)s,%(aggrfnc)s'),
        
        'print_': ([('vname', True),  ('format', False)], 'PRINT:%(vname)s:%(format)s'),
        'gprint': ([('vname', True),  ('format', False)], 'GPRINT:%(vname)s:%(format)s'),
        'comment': ([('text', True)], 'COMMENT:%(text)s'),
        
        'hrule': ([('value', True), ('color', True), ('legend', False)], 'HRULE:%(value)s#%(color)s:%(legend)s'),
        'vrule': ([('time', True), ('color', True), ('legend', False)], 'VRULE:%(value)s#%(color)s:%(legend)s'),
        
        'line1': (
            [('vname', True), ('color', False), ('legend', False), ('stack', False)], 
            {
                1: 'LINE1:%(vname)s',
                2: 'LINE1:%(vname)s#%(color)s',
                3: 'LINE1:%(vname)s#%(color)s:%(legend)s',
                4: 'LINE1:%(vname)s#%(color)s:%(legend)s:%(stack)s',
            }),
        'line2': (
            [('vname', True), ('color', False), ('legend', False), ('stack', False)], 'LINE2:%(vname)s#%(color)s:%(legend)s:%(stack)s',
            {
                1: 'LINE2:%(vname)s',
                2: 'LINE2:%(vname)s#%(color)s',
                3: 'LINE2:%(vname)s#%(color)s:%(legend)s',
                4: 'LINE2:%(vname)s#%(color)s:%(legend)s:%(stack)s',
            }),
        'line3': (
            [('vname', True), ('color', False), ('legend', False), ('stack', False)],
            {
                1: 'LINE3:%(vname)s',
                2: 'LINE3:%(vname)s#%(color)s',
                3: 'LINE3:%(vname)s#%(color)s:%(legend)s',
                4: 'LINE3:%(vname)s#%(color)s:%(legend)s:%(stack)s',
            }),
        'area': (
            [('vname', True), ('color', False), ('legend', False), ('stack', False)],
            {
                1: 'AREA:%(vname)s',
                2: 'AREA:%(vname)s#%(color)s',
                3: 'AREA:%(vname)s#%(color)s:%(legend)s',
                4: 'AREA:%(vname)s#%(color)s:%(legend)s:%(stack)s',
            }),
        }
    
    
    
    def __init__(self, data=None):
        self.params = []
        self.multi = []
        
        if data:
            for k, v in data:
                setattr(self, k, v)


    def __dir__(self):
        return [
            '__init__', 
            'graph',
            ] + Graph.SIMPLE_KEYWORDS.keys() + Graph.MULTI_KEYWORDS.keys()

    
    def __getattr__(self, attr):
        if attr in Graph.SIMPLE_KEYWORDS:
            def wrapper(name):
                self._set_param(attr, name)
            return wrapper
        if attr in Graph.MULTI_KEYWORDS:
            def wrapper(*args):
                self._set_multi(attr, *args)
            return wrapper
        if attr.startswith('get_'):
            return dict(self.params)[attr[4:]]

        return object.__getattr__(self, attr)
        
        
    
    def _set_multi(self, name, *args):
        '''
        Used to set complex values, such as DEF, LINE etc
        '''        
        try:
            row = {}
            kw = Graph.MULTI_KEYWORDS[name][0]
            
            it = iter(kw)
            
            for a in args:
                d = it.next()  
                row[d[0]] = a
              
            try:
                while True:
                    d = it.next()
                    if d[1]:
                        raise ValueError('Argument %s for value %s is required!' % (d[0], name))
                    row[d[0]] = ''
            except StopIteration:
                pass
                
            self.multi.append((name, row))
        except KeyError:
            raise KeyError('There is no such parameter in RRD graph (%s)' % name)
        
        
    
    def _set_param(self, name, value):
        '''
        This method sets the simple parameter value, based on SIMPLE_KEYWORDS dict
        It's applied for params like filename, width, start, etc.
        '''
        try:
            kw = Graph.SIMPLE_KEYWORDS[name][0]
            if type(kw) in (list, tuple):
                if value not in kw:
                    raise ValueError('There is no such value for %s (%s)' % ( name, value))
            else:
                if type(value) != kw:
                    raise ValueError('Wrong datatype for %s (got: %s, expected %s)' % (name, str(type(value)), str(kw)))
            
            self.params.append( (name, value) ) 
        except KeyError:
            raise KeyError('There is no such parameter in RRD graph (%s)' % name)

    
    def __setattr__(self, name, value):
        if name in ('params', 'multi'):
            object.__setattr__(self, name, value)
            return

        if type(value) in (list, tuple):
            self._set_multi(name, *value)
        else:
            self._set_param(name, value)
   
        
        
    def prepare_args(self):
        '''
        Generate list of arguments to be used in graphing
        '''
        args = []
        
        for k, v in self.params:
            prefix = Graph.SIMPLE_KEYWORDS[k][1]
            type_ = Graph.SIMPLE_KEYWORDS[k][0]
            
            if prefix:
                k = k.replace('_', '-')
                if type_ == bool and v:
                    args += [prefix + str(k)]
                else:
                    args += [prefix + str(k), str(v)]
            else:
                args.append(str(v))

        for k, v in self.multi:
            km = Graph.MULTI_KEYWORDS[k][1]
            if type(km) is dict:
                noa = sum([1 if a is not None else 0 for a in v.values()])
                if not noa in km:
                    raise ValueError('There is no template with this number of arguments (%i)' % noa)
                km = km[noa]
                args.append(km % v)
            else:
                args.append(km % v)
        
        return args
        
        
        
    def graph(self):
        '''
        Performs actual graphing
        '''
        import rrdtool           
        rrdtool.graph(*self.prepare_args())

    