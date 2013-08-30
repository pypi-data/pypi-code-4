#!/usr/bin/env python
from mocksey import mocksey_assert_equal

def tweak_mock():
    import mock
    from mock import call
    def mocksey_assert_called_once_with(self, *args, **kwargs):
        """assert that the mock was called exactly once and with the specified
        arguments.

        Mocksey copied this from voidspace's great "mock" and modified it for you:
          http://www.voidspace.org.uk/python/mock/
          That License:
            Copyright (c) 2003-2010, Michael Foord
            All rights reserved.
            E-mail : fuzzyman AT voidspace DOT org DOT uk
        """
        if not self.call_count == 1:
            raise AssertionError("Mock '{}' expected to be called once. Called {:d} times with {}.".format(self, self.call_count, self.call_args_list))
        return self.assert_called_with(*args, **kwargs)


    def mocksey_assert_any_call(self, *args, **kwargs):
        """assert the mock has been called with the specified arguments.

        The assert passes if the mock has *ever* been called, unlike
        `assert_called_with` and `assert_called_once_with` that only pass if
        the call is the most recent one.

        Mocksey copied this from voidspace's great "mock" and modified it for you:
          http://www.voidspace.org.uk/python/mock/
          That License:
            Copyright (c) 2003-2010, Michael Foord
            All rights reserved.
            E-mail : fuzzyman AT voidspace DOT org DOT uk
        """
        if self.call_count <= 1:
            self.assert_called_with(*args, **kwargs)
        else:
            kall = call(*args, **kwargs)
            if kall not in self.call_args_list:
                expected_string = self._format_mock_call_signature(args, kwargs)
                foo = self.call_args_list
                if self._mock_name:
                    foo = repr(self.call_args_list).replace('call(', self._mock_name + '(')
                raise AssertionError('{} call not found among:\n\t{}'.format(expected_string, foo))


    def mocksey_assert_called_with(self, *args, **kwargs):
        """assert that the mock was called with the specified arguments.

        Raises an AssertionError if the args and keyword args passed in are
        different to the last call to the mock.

        Mocksey copied this from voidspace's great "mock" and modified it for you:
          http://www.voidspace.org.uk/python/mock/
          That License:
            Copyright (c) 2003-2010, Michael Foord
            All rights reserved.
            E-mail : fuzzyman AT voidspace DOT org DOT uk
        """
        if not self.called:
            raise AssertionError("Mock '{}' was never called.".format(self))

        nofail = 'Nothing!'

        arg_out = nofail
        kwarg_out = nofail
        try:
            mocksey_assert_equal(args, self.call_args[0])
        except AssertionError as e:
            arg_out = str(e)

        try:
            mocksey_assert_equal(kwargs, self.call_args[1])
        except AssertionError as e:
            kwarg_out = str(e)

        if arg_out != nofail or kwarg_out != nofail:
            output = '{} Suffered the following call issues (expected != actual):\nArgs:  {}\nKwargs: {}'.format(self, arg_out, kwarg_out)
            raise AssertionError(output)


    mock.NonCallableMock.assert_called_once_with = mocksey_assert_called_once_with
    mock.NonCallableMock.assert_any_call = mocksey_assert_any_call
    mock.NonCallableMock.assert_called_with = mocksey_assert_called_with

    return mock

if __name__ == "__main__":
    import mock
    tweak_mock()
    foo = mock.MagicMock(name="past")
    foo('lollipop', rambo='doody')
    # foo('aosenuth', 'asoneuht2aou')
    foo.assert_called_once_with('aosenuth', 'asoneuht')
    # foo.assert_called_with('lollipoop', rambo='duty', zippo=True)
