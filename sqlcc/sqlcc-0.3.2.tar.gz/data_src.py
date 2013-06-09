import sql


def ds_define():
    import sys
    from pythk.types import is_subclass, is_lambda
    frame = sys._getframe(1)
    tables = [(key, value) for key, value in frame.f_locals.items() if is_subclass(value, sql.table)]
    vview_gen = [(key, value) for key, value in frame.f_locals.items() if is_lambda(value)]
    ds_queries = [(key, value) for key, value in frame.f_locals.items() if isinstance(value, ds_query)]
    return tables, vview_gen, ds_queries


# Data source query is a query function to execute an SQL query.
#
# The instance of ds_query is a callable for create an SQL command and
# sent to SQL server/database engine with the given arguments.  The
# arguments passed to the callable are used values of free variables
# in the query.  Free variables are appearances of sql._q in the
# definition of a query.
#
class ds_query(object):
    pass


# This class is supposed to be used as a decorator.
class vquery(ds_query):
    def __init__(self, vview_gen):
	self.vview_gen = vview_gen
        self.argcount = vview_gen.func_code.co_argcount
	pass
    
    def __get__(self, instance, owner):
        try:
            return instance.__cmds[self]
        except:
            pass

	def cmd(*args):
            assert len(args) == self.argcount

	    if hasattr(self, 'qstr'):
		qstr = self.qstr
                args_temp = self.args_temp
	    else:
                free_vars = [sql.free_var_temp(i)
                             for i in range(self.argcount)]
                vv = self.vview_gen(*free_vars)
		self.qstr = qstr = str(vv)
                self.args_temp = args_temp = vv.get_const_values()
		pass
            exec_args = [((isinstance(v, sql.free_var) and (args[v.idx],)) or
                          (v,))[0]
                         for v in args_temp]
	    cu = instance.get_cursor()
	    cu.execute(qstr, exec_args)
	    return cu.fetchone()[0]

        try:
            instance.__cmds[self] = cmd
        except AttributeError:
            instance.__cmds = {self: cmd}
            pass
	return cmd
    pass


class squery(ds_query):
    def __init__(self, field_names, vview_gen):
	self.field_names = field_names
	self.vview_gen = vview_gen
        self.argcount = vview_gen.func_code.co_argcount
	pass
    
    def __get__(self, instance, owner):
        try:
            return instance.__cmds[self]
        except:
            pass

	def cmd(*args):
            assert len(args) == self.argcount

	    from pythk.conveniences import combine_sequences
	    if hasattr(self, 'qstr'):
		qstr = self.qstr
                args_temp = self.args_temp
	    else:
                free_vars = [sql.free_var_temp(i)
                             for i in range(self.argcount)]
                vv = self.vview_gen(*free_vars)
		self.qstr = qstr = str(vv)
                self.args_temp = args_temp = vv.get_const_values()
		pass
            exec_args = [((isinstance(v, sql.free_var) and (args[v.idx],)) or
                          (v,))[0]
                         for v in args_temp]
	    cu = instance.get_cursor()
	    cu.execute(qstr, exec_args)
	    row = cu.fetchone()
	    return dict(combine_sequences(self.field_names, row))

        try:
            instance.__cmds[self] = cmd
        except AttributeError:
            instance.__cmds = {self: cmd}
            pass
	return cmd
    pass


# This function is a decorator for queries returning single row.
def squery_fs(*field_names):
    return lambda vview_gen: squery(field_names, vview_gen)


class mquery(ds_query):
    def __init__(self, field_names, vview_gen):
	self.field_names = field_names
	self.vview_gen = vview_gen
        self.argcount = vview_gen.func_code.co_argcount
	pass
    
    def __get__(self, instance, owner):
        try:
            return instance.__cmds[self]
        except:
            pass

	def cmd(*args):
            assert len(args) == self.argcount

	    from pythk.conveniences import combine_sequences
	    if hasattr(self, 'qstr'):
		qstr = self.qstr
                args_temp = self.args_temp
	    else:
                free_vars = [sql.free_var_temp(i)
                             for i in range(self.argcount)]
                vv = self.vview_gen(*free_vars)
		self.qstr = qstr = str(vv)
                self.args_temp = args_temp = vv.get_const_values()
		pass
            exec_args = [((isinstance(v, sql.free_var) and (args[v.idx],)) or
                          (v,))[0]
                         for v in args_temp]
	    cu = instance.get_cursor()
	    cu.execute(qstr, exec_args)
	    rows = cu.fetchall()
	    return [dict(combine_sequences(self.field_names, row)) for row in rows]

        try:
            instance.__cmds[self] = cmd
        except AttributeError:
            instance.__cmds = {self: cmd}
            pass
	return cmd
    pass


# This function is the decorator for queries returning multiple rows.
def mquery_fs(*field_names):
    return lambda vview_gen: mquery(field_names, vview_gen)


class data_src_meta(type):
    def __new__(M, name, bases, dict):
	try:
	    ds_definition = dict['ds_definition']
	except KeyError:
            all_tbs = [v for v in dict.values()
                       if isinstance(v, type) and issubclass(v, sql.table)]
            dict['_all_tbs'] = all_tbs
	else:
	    tables, vview_gens, ds_queries = ds_definition()
	    all_tbs = []
	    
	    del dict['ds_definition']
	    
	    for name, tb_class in tables:
		dict[name] = tb_class
		all_tbs.append(tb_class)
		pass
	    
	    for name, vview_gen in vview_gens:
		data_src = data_src_meta.make_query_cmd_from_view_gen(name, vview_gen)
		dict[name] = data_src
		pass
	    
	    for name, a_ds_query in ds_queries:
		dict[name] = a_ds_query
		pass
	    
	    dict['_all_tbs'] = all_tbs
	    pass
	
	return type.__new__(M, name, bases, dict)
    
    class make_query_cmd_from_view_gen(object):
	def __init__(self, var_name, view_generator):
	    self.var_name = var_name
	    self.view_generator = view_generator
	    pass
	
	def __get__(self, instance, owner):
	    def cmd(*args):
		if hasattr(self, 'qstr'):
		    qstr = self.qstr
		else:
		    qstr = str(self.view_generator())
		    self.qstr = qstr
		    pass
		cu = instance.get_cursor()
		cu.execute(qstr, args)
		return cu
	    
	    return cmd
	
	def __set__(self, instance, value):
	    raise AttributeError()
	
	def __delete__(self, instance):
	    raise AttributeError()
	pass
    pass


class data_src(object):
    __metaclass__ = data_src_meta
    
    def __init__(self, db_conn):
	super(data_src, self).__init__()
	self.cx = db_conn
	pass
    
    def init_db(self):
	cu = self.get_cursor()
	for tb in self._all_tbs:
	    qstr = tb.schema
	    cu.execute(qstr)
	    pass
	pass
    
    def insert(self, table, **kws):
	cu = self.get_cursor()
	cmd, args = apply(table.factory, (), kws).gen_insert_cmd()
	cu.execute(cmd, args)
	return cu
    
    def update(self, table, **kws):
	cu = self.get_cursor()
	if kws.has_key('where'):
	    cond = kws['where']
	    kws = dict(kws)
	    del kws['where']
	else:
	    cond = None
	    pass
	values_o = apply(table.factory, (), kws)
	
	cmd, args = values_o.gen_update_cmd(cond)
	cu.execute(cmd, args)
	return cu
    
    def delete(self, table, where=None):
	cu = self.get_cursor()
	cmd, args = table.gen_delete_cmd(where)
	cu.execute(cmd, args)
	return cu
    
    def get_cursor(self):
	return self.cx.cursor()
    
    def commit(self):
	self.cx.commit()
	pass
    
    def rollback(self):
	self.cx.rollback()
	pass
    
    @staticmethod
    def clone_tb(tb):
	assert isinstance(tb, sql.table)
	return tb.__class__()
    pass


if __name__ == '__main__':
    from sql import *
    from sql import _q
    
    class testds(data_src):
        def ds_definition():
            # Data model is defined in a function to leverage closure in
            # the definition of queries.
            class users(table):
                sn = int_f()
                name = str_f()
                balance = float_f()
                pass
    
            class transactions(table):
                sn = int_f()
                user = int_f()
                value = float_f()
                date = str_f()
                pass
    
            @mquery_fs('value', 'date')
            def user_trans(uname):
                u = users()
                t = transactions()
                return (u * t).fields(t.value, t.date).\
                    where((u.sn == t.user) & (u.name == uname))
    
            @mquery_fs('value', 'date')
            def snuser_trans(sn, uname):
                u = users()
                t = transactions()
                return (u * t).fields(t.value, t.date).\
                    where((u.name == uname) & (u.sn == sn))
    
            @vquery
            def user_balance(uname):
                u = users()
                return vview(u).fields(u.balance).where(u.name == uname)

            # ds_define() collects the definition of the data model.
            return ds_define()
        pass
    
    class dummy_cursor(object):
        def execute(self, *args):
            print
            print 'EXECUTE:'
            print args[0]
            if len(args) == 2:
                print 'ARGS:'
                print args[1]
                pass
            pass

        def fetchall(self, *args):
            return []

        def fetchone(self, *args):
            return [1]
        pass

    class dummy_cx(object):
        def commit(self):
            pass
        def rollback(self):
            pass
        def cursor(self):
            return dummy_cursor()
        pass

    cx = dummy_cx()
    ds = testds(cx)
    print ds.users.schema
    print ds.transactions.schema
    ds.init_db()
    ds.user_trans('test')
    ds.snuser_trans(1, 'test')
    ds.user_balance('test')
    ds.insert(ds.users, sn=1, name='user1', balance=0)
    ds.delete(ds.users, ds.users.sn == 333)
    pass
