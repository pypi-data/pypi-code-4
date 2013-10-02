import types, bisect
import IPython

dreload_excludes = ['sys', 'os.path', '__builtin__', '__main__', 'IPython']

def load_ipython_extension(ipython):
    """Called by %load_ext magic command to load this extension"""
    pass

def unload_ipython_extension(ipython):
    """Called by %unload_ext magic command to remove this extension"""
    pass

@IPython.core.magic.magics_class
class InstanceInstrospectionMagics(IPython.core.magic.Magics):
    """Magic functions related to object introspection.
    %pi, print instance"""

    @IPython.core.magic.line_magic
    def pi(self, line):
        """
        Print instance function
        Usage:
        - %pi object
        - %pi object pattern
        - %pi object pattern separator

        pattern = filter the property, basic test: 'pattern string contained in property name'
        if pattern == '*' nothing will be filtered
        default separator is new line.
        """
        def _pi(o, pattern='*', sep='\n'):
            def _p(d, o):
                output = list()
                for k in sorted(d.keys()):
                    val = repr(d[k])
                    append = True
                    if pattern != '*':
                        append = pattern in k
                    if append:
                        if sep != '\n':
                            output.append("%s= %s" % (k, val))
                        else:
                            output.append("%-15s= %-80.80s" % (k, val))
                return '%s\n%s' % (o, sep.decode('string_escape').join(output))
            if type(o) == dict:
                return _p(o, 'dict')
            else:
                return _p(o.__dict__, o)

        opts, arg = self.parse_options(line, '', mode='list')
        if not len(arg):
            return
        o = arg[0]
        if o in self.shell.user_ns:
            obj = self.shell.user_ns[o]
            kwargs = {}
            if len(arg) == 3:
                kwargs['pattern'] = arg[1]
                kwargs['sep'] = arg[2]
            elif len(arg) == 2:
                kwargs['pattern'] = arg[1]
            print _pi(obj, **kwargs)

try:
    ip = get_ipython()
    ip.register_magics(InstanceInstrospectionMagics)
except NameError:
    pass
