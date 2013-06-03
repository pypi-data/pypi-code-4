
import inspect
import os
from . import hook
from . import EPS


def get_args(node):
    method = node['method']
    if not inspect.isfunction(method):
        return ''
    gas = inspect.getargspec(method)
    delta = len(gas.defaults or []) - len(gas.args)
    def inject(d):
        i, value = d
        i += delta
        if i >= 0:
            value += '=' + repr(gas.defaults[i])
        return value
        
    return ', '.join(map(inject, enumerate(gas.args)))


def get_located(node):
    return os.path.relpath(node['located'][0]) + ':' + str(node['located'][1])


def info_eps_raw(instance):
    """Print EPS functional"""
    for method_name, cfg in sorted(instance._api.items(), key=lambda x:x[0]):
        if len(cfg) == 1:
            node = cfg[0]
            comment = node['comment']
            if not comment and hasattr(node['method'], '__doc__'): comment = str(getattr(node['method'], '__doc__') or '')
            yield ('method', node['priority'], method_name, get_args(node), get_located(node), comment)
        else:
            yield ('loop', method_name)
            for node in cfg:
                method = node['method']
                locname = 'do'
                if hasattr(method, '__name__'): locname = str(getattr(method, '__name__') or 'do')
                comment = node['comment']
                if not comment and hasattr(method, '__doc__'): comment = str(getattr(method, '__doc__') or '')
                yield ('node', node['priority'], locname, get_args(node), get_located(node), comment)


def info_print(self):
    """print functional"""
    templ = {
        'method': '%d %s(%s) [%s] %s',
        'loop': '%s <loop>',
        'node': '    %d %s(%s) [%s] %s'
    }
    for r in info_eps_raw(self.eps):
        t, row = r[0], r[1:]
        print(templ[t]%row)


def info_html(self):
    """return functional as html string"""
    templ = {
        'method': '<tr> <td><b>{1}</b></td> <td>{0}</td> <td>{2}</td> <td>{3}</td> <td>{4}</td> </tr>',
        'loop': '<tr> <td><b>{0}</b></td> <td></td> <td> &lt;loop&gt; </td> </tr>',
        'node': '<tr> <td></td> <td>{0}</td> <td>{1}({2})</td> <td>{3}</td> <td>{4}</td> </tr>'
    }
    html = ['<table><tr> <th>' + '</th><th>'.join(['Name', 'Pr', 'Args', 'Location', 'Comment']) + '</th></tr>']
    for r in info_eps_raw(self.eps):
        t, row = r[0], r[1:]
        html.append(templ[t].format(*row))
    html.append('</table>')
    return '\n'.join(html)


def pre_group(instance):
    tree = set()
    for r in info_eps_raw(instance):
        t, row = r[0], r[1:]
        if t == 'method':
            keys = row[1].split('.')
            # make path
            prefix = ''
            level = 0
            for key in keys[:-1]:
                prefix += key
                level += 1
                if prefix not in tree:
                    tree.add(prefix)
                    yield ('class', level, key)
            # make method
            yield ('method', level + 1, keys[-1], row[2], row[3], row[4])
        elif t == 'loop':
            keys = row[0].split('.')
            # make path
            prefix = ''
            level = 0
            for key in keys[:-1]:
                prefix += key
                level += 1
                if prefix not in tree:
                    tree.add(prefix)
                    yield ('class', level, key)
            # make method
            yield ('loop', level + 1, keys[-1])


def info_pypredef(self):
    src = []
    src.append('class EPS:')
    for r in pre_group(self.eps):
        t, row = r[0], r[1:]
        if t == 'class':
            level, name = row
            margin = '    '*level
            src.append('%sclass %s:'%(margin, name))
        elif t == 'method':
            level, name, args, located, comment = row
            margin = '    '*level
            src.append('%sdef %s(%s):'%(margin, name, args))
            src.append('%s    """'%margin)
            src.append('%s        %s'%(margin, comment))
            src.append('%s        %s'%(margin, located))
            src.append('%s    """'%margin)
        elif t == 'loop':
            level, name = row
            margin = '    '*level
            src.append('%sdef %s():'%(margin, name))
            src.append('%s    pass'%margin)
    
    return '\n'.join(src)

EPS.bind('eps.info_pypredef', info_pypredef)
EPS.bind('eps.info_print', info_print)
EPS.bind('eps.info_html', info_html)
EPS.bind('eps.Looper', hook.Looper, comment='class Looper')
EPS.bind('eps.set_looper', lambda cls:setattr(hook, 'DefaultLooper', cls), comment='Change default looper')
