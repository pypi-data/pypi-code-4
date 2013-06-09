'''
sql.py: Host SQL on Python Language

This module define a language for create data virtual views.  These
vviews are mapped to SELECT command of SQL.

table * table ==> vview
vview * table ==> vview

field + field ==> expr
expr + field ==> expr
'''
# 
# XXX: Please keep all sequence type attributes as list.
#      It eases our task that deepcopy an expr.
# XXX: Never duplicate SQL_field_type objects when performing
#      deepcopy.  SQL_field_type objects should be reused, or
#      remap to SQL_field_type objects of new tables.
#
import string
from copy import copy, deepcopy
from pythk import conveniences as cnv

def get_tables(*args):
    return tuple([table(x) for x in args])

# ============================================================
class operand(object):
    def __init__(self):
	super(operand, self).__init__()
	pass
    
    def get_sql_name(self):
	raise NotImplementedError()
    
    def get_sql_name_no_alias(self):
	raise NotImplementedError()

    def get_const_values(self):
        return ()
    
    def __str__(self):
	return self.op
    
    def __apply_binary(self, opstr, other):
	no = expr(self)
	no.children.append(op(opstr))
	no.children.append(normalize_operand(other))
	return no
    
    def __apply_unary(self, opstr):
	no = expr()
	no.children.append(op(opstr))
	no.children.append(self)
	return no
    
    def __add__(self, other):
	return self.__apply_binary('+', other)
    
    def __sub__(self, other):
	return self.__apply_binary('-', other)
    
    def __mul__(self, other):
	return self.__apply_binary('*', other)
    
    def __add__(self, other):
	return self.__apply_binary('/', other)
    
    def __eq__(self, other):
	return self.__apply_binary('=', other)
    
    def __ne__(self, other):
	return self.__apply_binary('!=', other)
    
    def __gt__(self, other):
	return self.__apply_binary('>', other)
    
    def __lt__(self, other):
	return self.__apply_binary('<', other)
    
    def __and__(self, other):
	return self.__apply_binary('AND', other)
    
    def __or__(self, other):
	return self.__apply_binary('OR', other)
    
    def __invert__(self):
	return self.__apply_unary('NOT')
    pass

class complex_operand(operand):
    children = []
    
    def __deepcopy__(self, memo):
	new_operand = copy(self)
	def only_dup_complex(child):
	    if not isinstance(child, complex_operand):
		return child
	    return deepcopy(child)
	new_operand.children = [only_dup_complex(child) for child in self.children]
	return new_operand
    
    def get_const_values(self):
        consts = ()
        for child in self.children:
            consts = consts + child.get_const_values()
            pass
        return consts
    pass

def normalize_operand(o):
    if isinstance(o, operand):
	return o
    return const(o)

class op(object):
    def __init__(self, op_name):
	super(op, self).__init__()
	self.op_name = op_name
	pass
    
    def get_sql_name(self):
	return self.op_name
    
    get_sql_name_no_alias = get_sql_name

    def get_const_values(self):
        return ()
    
    def __str__(self):
	return self.op_name
    pass

class func_generic(complex_operand):
    def __init__(self, *children):
	super(func_generic, self).__init__()
	self.children = [normalize_operand(child) for child in children]
	pass
    
    def get_sql_name(self):
	args = [c.get_sql_name() for c in self.children]
	arg_str = string.join(args, ', ')
	return self.__class__.__name__ + '(' + arg_str + ')'
    
    def get_sql_name_no_alias(self):
	args = [c.get_sql_name_no_alias() for c in self.children]
	arg_str = string.join(args, ', ')
	return self.__class__.__name__ + '(' + arg_str + ')'
    
    __str__ = get_sql_name
    pass

class foo(func_generic):
    pass

class isnull(func_generic):
    def get_sql_name(self):
	arg_str = self.children[0].get_sql_name()
	return arg_str + ' ISNULL'
    
    def get_sql_name_no_alias(self):
	arg_str = self.children[0].get_sql_name_no_alias()
	return arg_str + ' ISNULL'
    pass

class like(func_generic):
    def get_sql_name(self):
        children = self.children
        return '(' + children[0].get_sql_name() + ' like ' + \
            children[1].get_sql_name() + ')'

    def get_sql_name_no_alias(self):
        children = self.children
        return '(' + children[0].get_sql_name_no_alias() + ' like ' + \
            children[1].get_sql_name_no_alias() + ')'

class expr(complex_operand):
    def __init__(self, ex=None):
	super(expr, self).__init__()
	self.children = []
	if ex:
	    self.children.append(ex)
	    pass
	pass
    
    def __apply_binary(self, opstr, other):
	no = self.__class__(self)
	no.children.append(op(opstr))
	no.children.append(normalize_operand(other))
	return no
    
    def __apply_unary(self, opstr):
	no = self.__class__()
	no.children.append(op(opstr))
	no.children.append(self)
	return no
    
    def get_sql_name(self):
	return '(' + string.join(map(lambda x: x.get_sql_name(), self.children), ' ') + ')'
    
    def get_sql_name_no_alias(self):
	return '(' + string.join(map(lambda x: x.get_sql_name_no_alias(), self.children), ' ') + ')'

    def __str__(self):
	return self.get_sql_name_no_alias()
    pass

class const(operand):
    def __init__(self, v):
	super(const, self).__init__()
	self.value = v
	pass
    
    def __deepcopy__(self, memo):
	return const(self.value)
    
    def get_sql_name(self):
	import types
	if self.value is not None:
            return '?'
	return 'NULL'
    
    def get_sql_name_no_alias(self):
        return '?'

    def get_const_values(self):
        return (self.value,)
    
    def __str__(self):
	return repr(self.value)
    pass

# ============================================================
class sys_sym(operand):
    sym = None
    def __deepcopy__(self, memo):
	return self
    
    def get_sql_name(self):
	return self.sym
    
    get_sql_name_no_alias = get_sql_name
    
    def __str__(self):
	return self.sym
    pass

class all_sym(sys_sym):
    '''All symbol
    Used on count(*) to stand as all records.'''
    sym = '*'
    pass
_a = all_sym()

class free_var(sys_sym):
    '''Free variable (unknow)
    It is a place holder waiting for user code specifing
    data when executing the query.'''
    sym = '?'

    def get_const_values(self):
        return (self,)
    pass
_q = free_var()

class free_var_temp(free_var):
    def __init__(self, idx):
        super(free_var_temp, self).__init__()
        self.idx = idx
        pass
    pass

# =============================================================
class SQL_field_type(operand):
    '''Define data type of SQL
    User create a object of a child of SQL_field_type with field name to
    specify the field name & data type of the field.
    '''
    type_name = 'None'
    fmt_symbol = '%s'
    order_seq = 0
    
    def __init__(self, name=None, table=None):
	super(SQL_field_type, self).__init__()
	self.field_name = name
	self.pkey = False
	self.uniq = False
	self.autoinc = False
	self.seq = SQL_field_type.order_seq
	self.table = table
	SQL_field_type.order_seq = SQL_field_type.order_seq + 1
	pass
    
    def get_sql_name(self):
	return self.table.get_alias() + '.' + self.field_name
    
    def get_sql_name_no_alias(self):
	return self.field_name
    
    def primary(self, auto=False):
	self.pkey = True
	self.autoinc = auto
	return self
    
    def unique(self):
	self.uniq = True
	return self
    
    def __str__(self):
	return self.table.get_alias() + '.' + self.field_name
    
    def __deepcopy__(self, memo):
	return copy(self)
    
    @property
    def schema(self):
	if self.pkey:
	    ptn = '%s %s primary key'
	else:
	    ptn = '%s %s'
	    pass
	if self.autoinc:
	    ptn = ptn + ' autoincrement'
	    pass
	if self.uniq:
	    ptn = ptn + ' unique'
	    pass
	return ptn % (self.field_name, self.type_name)
    pass

class int_f(SQL_field_type):
    type_name = 'integer'
    fmt_symbol = '%d'
    pass

class float_f(SQL_field_type):
    type_name = 'float'
    fmt_symbol = '%f'
    pass

class date_f(SQL_field_type):
    type_name = 'date'
    pass

class str_f(SQL_field_type):
    type_name = 'text'
    pass

class primary_sn_f(SQL_field_type):
    type_name = 'integer primary key autoincrement'
    fmt_symbol = '%d'
    pass

# ============================================================
# constraints
class unique_c(object):
    def __init__(self, *args):
	super(unique_c, self).__init__()
	self.fields = args
	pass
    
    @property
    def schema(self):
	from string import join
	fnames = [f.get_sql_name_no_alias() for f in self.fields]
	return 'unique(' + join(fnames, ',') + ')'
    pass

def unique(*args):
    import sys
    frame = sys._getframe(1)
    ldict = frame.f_locals
    for f in args:
	if not isinstance(f, SQL_field_type):
	    raise ValueError('must be a squence of SQL_field_type instances')
	pass
    _uniques = ldict.setdefault('_unique_constraints', [])
    _uniques.append(unique_c(*args))
    ldict['_unique_constraints'] = _uniques
    pass


# ============================================================
class values(object):
    def __init__(self, table, kv_pairs):
	super(values, self).__init__()
	self.table = table
	self.kv_pairs = kv_pairs
	pass
    
    def gen_update_cmd(self, cond=None):
	return self.table.gen_update_cmd(self, cond)
    
    def gen_insert_cmd(self):
	return self.table.gen_insert_cmd(self)
    pass

class value_factory(object):
    def __init__(self, table):
	super(value_factory, self).__init__()
	self.table = table
	pass
    
    def __call__(self, **kws):
	table = self.table
	for key in kws:
	    if not isinstance(getattr(table, key), SQL_field_type):
		raise NameError('no such field (%s).' % (key,))
	    pass
	return values(self.table, kws.items())
    pass

# ============================================================
class table_meta(type):
    def __init__(cls, name, bases, dict):
	from pythk.types import is_descriptor
	super(table_meta, cls).__init__(name, bases, dict)
	
	cls.tab_name = name
	for key in dict:
	    o = dict[key]
	    if isinstance(o, SQL_field_type) and o.field_name == None:
		o.field_name = key
		pass
	    pass
	
	first_obj = cls()
	for key in dict:
	    o = dict[key]
	    if isinstance(o, SQL_field_type):
		setattr(cls, key, getattr(first_obj, key))
	    elif (not key.startswith('_')) and is_descriptor(o):
		# method is also a descriptor
		remap_o = cls._remap(o)
		setattr(cls, key, remap_o)
		pass
	    pass
	
	cls.__objs = [first_obj]
	pass
    
    def __getitem__(cls, idx):
	objs = cls.__objs
	if idx >= len(objs):
	    num = (idx - len(objs) + 4) & ~0x3
	    objs = cls.__objs = objs + ([None] * num)
	    pass
	obj = objs[idx]
	if not obj:
	    obj = objs[idx] = cls()
	    pass
	return obj
    
    def __mul__(cls, other):
	from pythk.types import is_subclass
	obj = cls[0]
	if is_subclass(other, table):
	    other = other[0]
	    pass
	return obj * other
    
    @property
    def _(cls):
	return cls[0]
    
    def __getattr__(cls, name):
	'''Redirect accessing to variable that not defined in class
	to first instance object.'''
	return getattr(cls.__objs[0], name)
    
    class _remap(object):
	'''Remap directly accessing to unbound method to
	bound method of first instance object, foo_table.__objs[0].'''
	def __init__(self, src):
	    super(table_meta._remap, self).__init__()
	    self.src = src
	    pass
	
	def __get__(self, instance, owner):
	    src = self.src
	    if instance:
		tgt = src.__get__(instance, owner)
	    else:
		tgt = src.__get__(owner[0], owner)
		pass
	    return tgt
	pass
    pass
	
class table(object):
    __metaclass__ = table_meta
    def __init__(self, name=None, fields=[]):
	object.__init__(self)
	
	cdict = self.__class__.__dict__
	predefined = [cdict[key] for key in cdict if isinstance(cdict[key], SQL_field_type)]
	if name != None:
	    self.tab_name = name
	    pass
	apply(self.set_fields, tuple(predefined) + tuple(fields))
	self.factory = value_factory(self)
	self.alias = 'A%x' % (id(self),)
	self.copy_from = self
	self.copies = 0
	pass
    
    def get_alias(self):
	return self.alias
    
    def set_fields(self, *fields):
	self.__fields = [copy(f) for f in fields]
	for f in self.__fields:
	    setattr(self, f.field_name, f)
	    f.table = self
	pass
    
    def _values_2_assigns(self, values):
	kv_pairs = values.kv_pairs
	assigns = []
	for k, v in kv_pairs:
	    field = getattr(self, k)
	    if not isinstance(field, SQL_field_type):
		raise TypeError('%s.%s is not a SQL_field_type object.' % (self.__class__.name, k))
	    v = normalize_operand(v)
	    ass = '%s=%s' % (field.get_sql_name_no_alias(), v.get_sql_name_no_alias())
	    assigns.append(ass)
	    pass
	return assigns
    
    def gen_update_cmd(self, values, cond=None):
	from string import join
	assigns = self._values_2_assigns(values)
	a_str = join(assigns, ', ')
	cmd = 'update %s set %s' % (self.tab_name, a_str)
        origin_values = [normalize_operand(v) for k, v in values.kv_pairs]
        args = tuple([v.value for v in origin_values if isinstance(v, const)])
	if cond:
	    cmd = cmd + ' where ' + cond.get_sql_name_no_alias()
            args = args + cond.get_const_values()
	    pass
	return cmd, args
    
    def gen_update_from_vview_cmd(self, values, fields=None, where=None):
	raise NotImplementedError()
    
    def gen_insert_cmd(self, values):
	from string import join
	_keys = string.join([getattr(self, k).get_sql_name_no_alias() for k, v in values.kv_pairs], ', ')
        origin_values = [normalize_operand(v) for k, v in values.kv_pairs]
	_values = string.join([v.get_sql_name_no_alias() for v in origin_values], ', ')
	cmd = 'insert into %s (%s) values(%s)' % (self.tab_name, _keys, _values)
        args = tuple([v.value for v in origin_values if isinstance(v, const)])
	return cmd, args
    
    def gen_delete_cmd(self, where=None):
	from string import join
	cmd = 'delete from ' + self.tab_name
	if where:
	    cmd = cmd + ' where ' + where.get_sql_name_no_alias()
	    pass
        args = where.get_const_values()
	return cmd, args
    
    def __mul__(self, other):
	return vview(self, other)
    
    def __str__(self):
	return '<table ' + self.tab_name + '>'
    
    def __deepcopy__(self, memo):
	new_tab = copy(self)
	apply(new_tab.set_fields, self.__fields)
	new_tab.factory = value_factory(self)
	orig = self.copy_from
	new_tab.alias = '%s_%04x' % (orig.alias, orig.copies)
	orig.copies = orig.copies + 1
	return new_tab
    
    @property
    def schema(self):
	fields = list(self.__fields)
	fields.sort(cmp=cnv.cmp_by_attr('seq'))
	fields = fields + getattr(self, '_unique_constraints', [])
	return 'create table ' + self.tab_name + '(\n\t' +string.join([x.schema for x in fields], ',\n\t') + '\n\t);\n'
    pass


# ============================================================
class vview(object):
    def __init__(self, *args):
	super(vview, self).__init__()
	self.__members = list(args)
	self.__fields = []
	self.__cond = []
	self.__group = []
	self.__order = []
	pass
    
    def __mul__(self, other):
	# don't join a table object more than once.
	self.__members.append(other)
	return self
    
    def __str__(self):
	return self.make_query_str()
    
    def __deepcopy__(self, memo):
	new_view = vview()
	new_view.__members = deepcopy(self.__members)
	
	new_view.__fields = deepcopy(self.__fields)
	new_view.__cond = deepcopy(self.__cond)
	new_view.__group = deepcopy(self.__group)
	new_view.__order = deepcopy(self.__order)
	
	self.__link_fields_to_new_tables(new_view, self.__members, new_view.__members)
	
	return new_view

    def get_const_values(self):
        values = ()
        for c in self.__cond:
            values = values + c.get_const_values()
            pass
        return values
    
    def make_query_str(self, restrict=None):
	tbs = string.join(map(lambda x: x.tab_name + ' ' + x.get_alias(), self.__members), ', ')
	if self.__fields:
	    fds = string.join(map(lambda x: x.get_sql_name(), self.__fields), ', ')
	else:
	    fds = '*'
	    pass
	if self.__cond:
	    conds = [c.get_sql_name() for c in self.__cond]
	    conds = '(' + string.join(conds, ') AND (') + ')'
	else:
	    conds = ''
	    pass
	if restrict:
	    if conds:
		conds = conds + ' AND (' + restrict.get_sql_name() + ')'
	    else:
		conds = restrict.get_sql_name()
		pass
	    pass
	if conds:
	    conds = ' where ' + conds
	    pass
	if self.__order:
	    orders = ' order by ' + string.join([o.get_sql_name() for o in self.__order], ', ')
	else:
	    orders = ''
	    pass
	return 'select ' + fds + ' from ' + tbs + conds + orders
    
    def join_on(self, cond):
	pass
    
    def ljoin_on(self, cond):
	pass
    
    def where(self, cond):
	self.__cond.append(cond)
	return self
    
    def group(self, *fields):
	self.__group = fields
	return self
    
    def order(self, *order):
	self.__order = order
	return self
	
    def fields(self, *args):
	self.__fields = list(args)
	return self
    
    @staticmethod
    def __link_fields_to_new_tables(view, old_tables, new_tables):
	from pythk.tourist import isinstance_tourist, isinstance_act
	from pythk.conveniences import combine_sequences
	class replace_field_act:
	    def __init__(self, tab_map):
		self.tab_map = tab_map
		self.visited = {}
		pass
	    
	    def __call__(self, visit):
		field = visit.obj
		field_name = field.field_name
		old_table = field.table
		new_table = self.tab_map[old_table]
		
		parent = visit.parent.obj
		attr_name = visit.name
		new_field = getattr(new_table, field_name)
		if isinstance(getattr(parent, attr_name), list):
		    getattr(parent, attr_name)[visit.idx] = new_field
		else:
		    setattr(parent, attr_name, new_field)
		    pass
		return None
	    pass
	
	tab_map = combine_sequences(old_tables, new_tables)
	tab_map = dict(tab_map)
	replacer = replace_field_act(tab_map)
	def skip(x):
	    return None
	
	actions = []
	actions.append(isinstance_act((SQL_field_type,), replacer))
	actions.append(isinstance_act((table, property), skip))
	tour = isinstance_tourist(actions)
	
	tour.walk(None, view)
	pass
    pass


# ============================================================
if __name__ == '__main__':
    class table1(table):
	f1 = int_f()
	f2 = str_f()
	f3 = float_f()
	pass
    
    class table2(table):
	pass
    
    class table3(table):
	pass
    
    t1 = table1()
    t2 = table2()
    t3 = table3()
    t1.alias = 'A01'
    t2.alias = 'A02'
    t3.alias = 'A03'
    
    view = t1 * t2 * t3
    view.fields(t1.f1, foo(t1.f2)).where((t1.f1 == 'abc') & (foo(t1.f2) < t1.f3) & (t1.f3 > 4) & (t1.f2 == _q))
    print 'Virtual view =============================='
    print str(view)
    print 'Arguments ================================='
    print view.get_const_values()
    print 'Schema ===================================='
    print t1.schema
    print 'Deepcopy table ============================'
    print deepcopy(t1).schema
    print 'Deepcopy vview ============================'
    print str(deepcopy(view))
    print 'Gen_update_cmd ============================'
    print t1.factory(f1=_q, f2='aa', f3=11.5).gen_update_cmd(t1.f2=='ff')
    print 'Gen_insert_cmd ============================'
    print t1.factory(f1=1, f2='aa', f3=11.5).gen_insert_cmd()
    print 'Gen_delete_cmd ============================'
    print t1.gen_delete_cmd((t1.f1 == 3) & like(t1.f2, '%pattern%'))
    pass

