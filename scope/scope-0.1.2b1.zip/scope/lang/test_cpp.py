#
# lang/test_cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See file LICENSE)
#

# pylint: disable=C0111

import unittest
from .. import scope
from . import cpp


class TestCppSerializer(unittest.TestCase):  # pylint: disable-msg=R0904
    def test_cpp_serializer_1(self):
        template = cpp.tfile[
            '#include <string>'
        ]

        expected = """#include <string>\n"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_2(self):
        template = cpp.tfile[
            cpp.tclass('Foo')
        ]

        expected = """class Foo {\n}; // class Foo\n"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_3(self):
        template = cpp.tfile[
            cpp.tclass(
                'Foo',
                superclasses=[(cpp.PUBLIC, 'Bar'), (cpp.PRIVATE, 'Baz')]
            )
        ]

        expected = """class Foo : public Bar, private Baz {
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_4(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo')[
                cpp.tclass('Bar')
            ]
        ]

        expected = """
class Foo {
    class Bar {
    }; // class Bar
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_5(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo')[
                cpp.tclass('Bar'),
                cpp.tclass('Baz', visibility=cpp.PUBLIC)
            ]
        ]

        expected = """
class Foo {
    class Bar {
    }; // class Bar
public:
    class Baz {
    }; // class Baz
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_6(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo'),
            cpp.tclass('Bar')
        ]

        expected = """
class Foo {
}; // class Foo
class Bar {
}; // class Bar
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_7(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace('Baz')[
                cpp.tclass('Foo'),
                cpp.tclass('Bar')
            ]
        ]

        expected = """
namespace Baz {
    class Foo {
    }; // class Foo
    class Bar {
    }; // class Bar
} // namespace Baz
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_8(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace('A'),
            cpp.tnamespace('B')
        ]

        expected = """
namespace A {
} // namespace A
namespace B {
} // namespace B
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_9(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct('Foo')[
                cpp.tstruct('Bar')
            ]
        ]

        expected = """
struct Foo {
    struct Bar {
    }; // struct Bar
}; // struct Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_10(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct('Foo')[
                cpp.tstruct('Bar'),
                cpp.tstruct('Baz', visibility=cpp.PRIVATE)
            ]
        ]

        expected = """
struct Foo {
    struct Bar {
    }; // struct Bar
private:
    struct Baz {
    }; // struct Baz
}; // struct Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_11(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace
        ]

        expected = """
namespace {
} // namespace
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_12(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo')[
                scope.nothing
            ]
        ]

        expected = """
void foo() {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_13(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a'])[
                scope.nothing
            ]
        ]

        expected = """
void foo(int a) {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_14(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'])[
                scope.nothing
            ]
        ]

        expected = """
void foo(int a, string b) {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_15(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'],
                        virtual=True, const=True)[
                scope.nothing
            ]
        ]

        expected = """
virtual void foo(int a, string b) const {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_16(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('int', 'foo')[
                'return 42;'
            ]
        ]

        expected = """
int foo() {
    return 42;
}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_17(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tmethod('int', 'foo')[
                    scope.nothing
                ]
            ]
        ]

        expected = """
class A {
    int foo() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_18(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tmethod('int', 'foo', visibility=cpp.PUBLIC)[
                    scope.nothing
                ]
            ]
        ]

        expected = """
class A {
public:
    int foo() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_19(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tattribute('int', 'var')
            ]
        ]

        expected = """
class A {
    int var;
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_20(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tattribute('int', 'var', visibility=cpp.PUBLIC,
                               const=True)
            ]
        ]

        expected = """
class A {
public:
    const int var;
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_21(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tctor('A', visibility=cpp.PUBLIC)[
                    '// do nothing'
                ],
                cpp.tctor('A', ['const A & other'])[
                    scope.nothing
                ]
            ]
        ]

        expected = """
class A {
    A(const A & other) {}
public:
    A() {
        // do nothing
    }
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_22(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tdtor('~A', virtual=True)[
                    scope.nothing
                ]
            ]
        ]

        expected = """
class A {
    virtual ~A() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_23(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tenum('A', ['B', 'C', 'D'])
        ]

        expected = """
enum A {
    B,
    C,
    D
};
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_24(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tenum('A', [])
        ]

        expected = """
enum A {};
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_25(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'])
        ]

        expected = """
void foo(int a, string b);
"""

        self.assertEqual(scope.serialize(template), expected)
        
    def test_example_1(self):
        expected = cpp.tfile [
            '#include <string>',

            cpp.tclass(name='App') [
                cpp.tattribute('std::string', '_name'),
                cpp.tmethod('std::string', 'GetName', visibility=cpp.PUBLIC,
                            const=True) [
                    'return this->_name;'
                ],
                cpp.tmethod('void', 'SetName', ['const std::string & value'],
                            visibility=cpp.PUBLIC) [
                    'this->_name = value;'
                ]
            ]
        ]

        def my_property(attr_type, attr_name, camel_name):
            getter_name = 'Get{0}'.format(camel_name)
            setter_name = 'Set{0}'.format(camel_name)
            setter_arg = 'const {0} & value'.format(attr_type)

            return scope.span[
                cpp.tattribute(attr_type, attr_name),

                cpp.tmethod(attr_type, getter_name, visibility=cpp.PUBLIC,
                            const=True)[
                    'return this->{0};'.format(attr_name)
                ],

                cpp.tmethod('void', setter_name, [setter_arg],
                            visibility=cpp.PUBLIC)[
                    'this->{0} = value;'.format(attr_name)
                ]
            ]

        template = cpp.tfile[
            '#include <string>',
            cpp.tclass(name='App')[
                my_property('std::string', '_name', 'Name')
            ]
        ]

        self.assertEqual(scope.flatten(template), scope.flatten(expected))

    def test_custom_serialization_1(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace(name='A')[
                cpp.tnamespace(name='B')
            ]
        ]

        expected = """
namespace A
{
    namespace B
    {
    } // namespace B
} // namespace A
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OPEN_BRACE_IN_NEW_LINE_FOR_NAMESPACES: True
        }

        self.assertEqual(scope.serialize(template, options), expected)

    def test_custom_serialization_2(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace(name='A')[
                cpp.tnamespace(name='B')
            ]
        ]

        expected = """
namespace A {
    namespace B {
    }
}
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OMIT_COMMENT_AFTER_END_BRACE_NAMESPACES: True
        }

        self.assertEqual(scope.serialize(template, options), expected)

    def test_custom_serialization_3(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass(name='A')
        ]

        expected = """
class A
{
}; // class A
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OPEN_BRACE_IN_NEW_LINE_FOR_TYPES: True
        }

        self.assertEqual(scope.serialize(template, options), expected)

    def test_custom_serialization_4(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct(name='A')
        ]

        expected = """
struct A
{
}; // struct A
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OPEN_BRACE_IN_NEW_LINE_FOR_TYPES: True
        }

        self.assertEqual(scope.serialize(template, options), expected)

    def test_custom_serialization_5(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct(name='A')
        ]

        expected = """
struct A {
};
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OMIT_COMMENT_AFTER_END_BRACE_TYPES: True
        }

        self.assertEqual(scope.serialize(template, options), expected)

    def test_custom_serialization_6(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo') [
                '// do nothing'
            ]
        ]

        expected = """
void foo()
{
    // do nothing
}
"""

        options = scope.SerializerOptions()
        options.extras['cpp'] = {
            cpp.OPEN_BRACE_IN_NEW_LINE_FOR_METHODS: True
        }

        self.assertEqual(scope.serialize(template, options), expected)


if __name__ == '__main__':
    unittest.main()
