# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from LMIUtil import lmi_raise_or_dump_exception

from LMIExceptions import LMIDeletedObjectError

class lmi_return_expr_if_fail(object):
    """
    Decorator, which calls a specified expression and returns its return value instead of
    calling the decorated method, if provided test expression is False; otherwise a method
    is called.

    Example of usage:
        class Foo:
            def __init__(self, member):
                self._member = member

            def failed(self):
                print "expression failed"
                return False

            # NOTE: the self parameter to the method call needs to be passed via expr_ret_args,
            # therefore, there is a dummy lambda obj: obj, which is basically self variable.
            @lmi_return_expr_if_fail(lambda obj: obj._member, failed, lambda obj: obj)
            def some_method(self):
                print "some_method called"
                return True

        f = Foo(None)
        f.some_method() == False

        f = Foo(True)
        f.some_method() == True
    """
    def __init__(self, expr_test, expr_ret, Self=False, *expr_ret_args, **expr_ret_kwargs):
        """
        Constructs a lmi_return_expr_if_fail decorator object.

        Arguments:
            expr_test -- expression which determines, if to execute a return
                value expression
            expr_ret -- expression, which is called, if the expr_test returns False
            expr_ret_args -- expr_ret position arguments
            expr_ret_kwargs -- expr_ret keyword arguments
            Self -- bool flag, which specifies, if to pass "self" variable to the expr_ret,
                if expr_test failed
        """
        self._expr_test = expr_test
        self._expr_ret = expr_ret
        self._expr_ret_pass_self = Self
        self._expr_ret_args = expr_ret_args
        self._expr_ret_kwargs = expr_ret_kwargs

    def __call__(self, fn):
        """
        Executes a method call, if the test passed.

        Arguments:
            fn -- decorated method
        """
        def wrapper(self_wr, *args, **kwargs):
            failed = False
            try:
                if not self._expr_test(self_wr):
                    failed = True
            except AttributeError, e:
                failed = True
            if failed:
                if self._expr_ret_pass_self:
                    return self._expr_ret(self_wr, *self._expr_ret_args, **self._expr_ret_kwargs)
                return self._expr_ret(*self._expr_ret_args, **self._expr_ret_kwargs)
            return fn(self_wr, *args, **kwargs)
        return wrapper

class lmi_return_val_if_fail(lmi_return_expr_if_fail):
    """
    Decorator, which returns a specified value and no method call is performed, if
    provided test expression is False; otherwise a method is called.

    Example of usage:
        class Foo:
            def __init__(self, member):
                self._member = member

            @lmi_return_val_if_fail(lambda obj: obj._member, False)
            def some_method(self):
                print "some_method called"
                return True

        f = Foo(None)
        f.some_method() == False

        f = Foo(True)
        f.some_method() == True
    """
    def __init__(self, expr_test, rval):
        """
        Constructs a lmi_return_val_if_fail object.

        Arguments:
            expr_test -- if the expression returns False, a method call is called
            rval -- return value of the method, if the object attribute as expression
                failed
        """
        lmi_return_expr_if_fail.__init__(self, expr_test, lambda: rval)

class lmi_return_if_fail(lmi_return_val_if_fail):
    """
    Decorator, which returns None and no method call is performed, if provided test
    expression is False; otherwise a method is called.

    Example of usage:
        class Foo:
            def __init__(self, member):
                self._member = member

            @lmi_return_if_fail(lambda obj: obj._member)
            def some_method(self):
                print "some_method called"
                return True

        f = Foo(None)
        f.some_method() == None

        f = Foo(True)
        f.some_method() == True
    """
    def __init__(self, expr_test):
        """
        Constructs a lmi_return_if_fail decorator object.

        Arguments:
            expr_test -- if the expression returns True, a method call is called
        """
        lmi_return_val_if_fail.__init__(self, expr_test, None)

class lmi_possibly_deleted(lmi_return_expr_if_fail):
    """
    Decorator, which returns None, if provided test expression is True.

    Example of usage:
        class Foo:
            def __init__(self, deleted):
                self._deleted = deleted

            @lmi_possibly_deleted(lambda obj: obj._member, lambda: False)
            def some_method(self):
                print "some_method called"
                return True

        f = Foo(None)
        f.some_method() == False

        f = Foo(True)
        f.some_method() == True
    """
    def __init__(self, expr_ret, Self=False, *expr_ret_args, **expr_ret_kwargs):
        """
        Constructs a lmi_possibly_deleted object."

        Arguments:
            expr_ret -- callable or return value used, if expr_test fails
            expr_ret_args -- expr_ret position arguments
            expr_ret_kwargs -- expr_ret keyword arguments
            Self -- bool flag, which specifies, if to pass "self" variable to the expr_ret,
                if expr_test failed
        """
        call_expr = expr_ret if callable(expr_ret) else lambda: expr_ret
        lmi_return_expr_if_fail.__init__(self, lambda obj: not obj._deleted,
            call_expr, Self=Self, *expr_ret_args, **expr_ret_kwargs)

    def __call__(self, fn):
        """
        Executes a method call, if the test passed. If the test expression
        returns False, specified return value in the constructor is returned.
        If the LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            LMIDeletedObjectError

        Arguments:
            fn -- decorated method
        """
        def wrapper(self_wr, *args, **kwargs):
            failed = False
            try:
                if not self._expr_test(self_wr):
                    failed = True
            except AttributeError, e:
                failed = True
            if failed:
                errorstr = "This instance has been deleted from a CIM broker"
                lmi_raise_or_dump_exception(LMIDeletedObjectError(errorstr))
                if self._expr_ret_pass_self:
                    return self._expr_ret(self_wr, *self._expr_ret_args, **self._expr_ret_kwargs)
                return self._expr_ret(*self._expr_ret_args, **self._expr_ret_kwargs)
            return fn(self_wr, *args, **kwargs)
        return wrapper

def lmi_class_fetch_lazy(fn):
    """
    Decorator for LMIClass, which first fetches a wrapped CIMClass object and then
    executes a wrapped method.

    Arguments:
        fn -- wrapped method
    """
    def wrapped(self, *args, **kwargs):
        if not self._cim_class:
            self.fetch()
        return fn(self, *args, **kwargs)
    return wrapped
