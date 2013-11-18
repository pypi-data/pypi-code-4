from with_test import *
import inject_methods

if __name__ == '__main__':
    with test("some"):
        (1).must_equal(1)
        (1).must_equal(2)
        # raise "some"
        pass