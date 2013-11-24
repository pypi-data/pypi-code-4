
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


def node_to_dict(node, name=None):
    method = node['method']
    comment = node['comment']
    if not comment and hasattr(method, '__doc__'):
        comment = (method.__doc__ or '')
        if isinstance(comment, bytes):
            comment = comment.decode('utf8')
    if not name and hasattr(method, '__name__'):
        name = method.__name__
    package = ''
    module = inspect.getmodule(method)
    if module:
        package = module.__package__
    return {
        'name': name or u'<no_name>',
        'type': u'method',
        'priority': node['priority'],
        'args': get_args(node),
        'located': os.path.relpath(node['located'][0]) + ':' + str(node['located'][1]),
        'full_path': node['located'][0],
        'path': os.path.relpath(node['located'][0]),
        'comment': comment,
        'package': package,
        'node': node
    }


def info_eps_dict(instance):
    """Print EPS functional"""
    for name, line in sorted(instance._api.items(), key=lambda x:x[0]):
        if len(line) == 1:
            yield node_to_dict(line[0], name=name)
        else:
            lp = {
                'name': name,
                'type': 'loop',
                'list': map(node_to_dict, line)
            }
            yield lp


def pre_group(instance):
    tree = set()
    for node in info_eps_dict(instance):
        keys = node['name'].split('.')
        # make path
        prefix = ''
        level = 0
        for key in keys[:-1]:
            prefix += key + u'.'
            level += 1
            if prefix not in tree:
                tree.add(prefix)
                yield ('class', level, key)
        node['name'] = keys[-1]
        yield ('node', level, node)


def make_import(node):
    if node['path'].startswith(u'../'):
        if not node['package']:
            return u''
        d = node['package'].split('.')
    else:
        s = node['path']
        assert s[-3:] == '.py'
        s = s[:-3]
        d = s.split('/')
        if d[-1] == '__init__':
            d = d[:-1]

    if not d:
        return u''
    elif len(d) == 1:
        return u"import " + d[0]
    return u"from %s import %s" % (u'.'.join(d[:-1]), d[-1])


def info_pypredef(self, name='EPS'):
    src = []
    src.append('class %s:'%name)
    for t, level, node in pre_group(self.eps):
        if t == 'class':
            margin = '    '*level
            src.append('%sclass %s:'%(margin, node))
        elif t == 'node':
            level += 1
            if node['type'] == 'method':
                margin = u'    '*level
                src.append(u'%sdef %s(%s):'%(margin, node['name'], node['args']))
                src.append(u'%s    """'%margin)
                src.append(u'%s        %s'%(margin, node['comment']))
                src.append(u'%s        %s'%(margin, node['located']))
                src.append(u'%s    """'%margin)
                src.append(margin + u'    ' + make_import(node))
                src.append(u'')
            elif node['type'] == 'loop':
                margin = u'    '*level
                src.append(u'%sdef %s():'%(margin, node['name']))
                src.append(u'%s    pass'%margin)
                margin += u'    '
                for cn in node['list']:
                    src.append(u"%s\" %d %s(%s) from %s\"" % (margin, cn['priority'], cn['name'], cn['args'], cn['located']))
                    src.append(margin + make_import(cn))
                src.append(u'')

    return '\n'.join(src)


EPS.bind('eps.info_pypredef', info_pypredef)
EPS.bind('eps.Looper', hook.Looper, comment='class Looper')
EPS.bind('eps.set_looper', lambda cls:setattr(hook, 'DefaultLooper', cls), comment='Change default looper')
