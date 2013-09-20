import zuice.reflect

def test_class_with_no_explicit_constructor_has_no_arg_constructor():
    class Empty(object):
        pass
        
    assert zuice.reflect.has_no_arg_constructor(Empty)


def test_class_no_arg_constructor_is_recognised_as_no_arg_constructor():
    class Boring(object):
        def __init__(self):
            pass
        
    assert zuice.reflect.has_no_arg_constructor(Boring)



def test_class_constructor_with_args_is_not_recognised_as_no_arg_constructor():
    class SampleObject(object):
        def __init__(self, first, second=None, third=30):
            pass

    assert not zuice.reflect.has_no_arg_constructor(SampleObject)
