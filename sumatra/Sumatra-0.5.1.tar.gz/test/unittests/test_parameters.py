"""
Unit tests for the sumatra.parameters module
"""
from __future__ import with_statement
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
from copy import deepcopy
try:
    import json
except ImportError:
    import simplejson as json
from textwrap import dedent
from sumatra.parameters import SimpleParameterSet, JSONParameterSet, \
        NTParameterSet, ConfigParserParameterSet, build_parameters, \
        YAMLParameterSet, yaml_loaded


class TestNTParameterSet(unittest.TestCase):

    def setUp(self):
        self.example = {
                    "y": {
                        "a": -2,
                        "b": [4, 5, 6],
                        "c": 5,
                    },
                    "x": 2.9,
                    "z": 100,
                    "mylabel": "camelot",
                    "have_horse": False,
        }

    def test__json_should_be_accepted(self):
        P = NTParameterSet(json.dumps(self.example))
        self.assertEqual(P.y.a, -2)
        self.assertEqual(P.y.b, [4, 5, 6])
        self.assertEqual(P.x, 2.9)
        self.assertEqual(P.mylabel, "camelot")

    def test__str(self):
        P = NTParameterSet(self.example)
        as_string = str(P)
        self.assertIsInstance(as_string, basestring)
        self.assertEqual(P, NTParameterSet(as_string))
    
    def test__pop(self):
        P = NTParameterSet(self.example)
        self.assertEqual(P.pop('x'), 2.9)
        self.assertEqual(P.pop('have_horse'), False)
        self.assertEqual(P.pop('y'), {"a": -2,
                                      "b": [4, 5, 6],
                                      "c": 5})
        self.assertEqual(P.as_dict(), {'z': 100, 'mylabel': 'camelot'})


class TestSimpleParameterSet(unittest.TestCase):

    def test__init__should_accept_space_around_equals(self):
        P = SimpleParameterSet("x = 2\ny = 3")
        self.assertEqual(P["x"], 2)
        self.assertEqual(P["y"], 3)

    def test__init__should_accept_no_space_around_equals(self):
        P = SimpleParameterSet("x=2")
        self.assertEqual(P["x"], 2)

    def test__init__should_accept_hash_as_comment_character(self):
        P = SimpleParameterSet("x = 2 # this is a comment")
        self.assertEqual(P["x"], 2)

    def test__init__should_accept_an_empty_initializer(self):
        P = SimpleParameterSet("")
        self.assertEqual(P.values, {})

    def test__init__should_accept_dict(self):
        P = SimpleParameterSet({'x': 2, 'y': 3})
        self.assertEqual(P["x"], 2)
        self.assertEqual(P["y"], 3)

    def test__init__should_accept_a_filename_or_string(self):
        init = "x = 2\ny = 3"
        P1 = SimpleParameterSet(init)
        with open("test_file", "w") as f:
            f.write(init)
        P2 = SimpleParameterSet("test_file")
        self.assertEqual(P1.values, P2.values)
        os.remove("test_file")

    def test__init__should_raise_a_TypeError_if_initializer_is_not_a_filename_or_string(self):
        self.assertRaises(TypeError, SimpleParameterSet, [])

    def test__init__should_ignore_empty_lines(self):
        init = "x = 2\n\n\r   \ny = 3\n\n\r\t\t  \n"
        P = SimpleParameterSet(init)
        self.assertEqual(P["x"], 2)
        self.assertEqual(P["y"], 3)

    def test__init__should_ignore_comment_lines(self):
        init = "#some parameters\nx = 2\n# this is a comment at column 0\n  # this is an indented comment\n  y = 3"
        P = SimpleParameterSet(init)
        self.assertEqual(P["x"], 2)
        self.assertEqual(P["y"], 3)

    def test__init__should_raise_syntaxerror_if_line_doesnt_contain_param_or_comment(self):
        init = "# some data\n1.0 2.0 3.0\n4.0 5.0 6.0"
        self.assertRaises(SyntaxError, SimpleParameterSet, init)

    def test__string_parameters_should_be_able_to_contain_equals_signs(self):
        init = 'equation = "e = mc^2"'
        P = SimpleParameterSet(init)

    def test__getitem__should_give_access_to_parameters(self):
        P = SimpleParameterSet("x = 2\ny = 3")
        self.assertEqual(P["x"], 2)
        self.assertEqual(P["y"], 3)

    def test__getitem__should_raise_a_KeyError_for_a_nonexistent_parameter(self):
        P = SimpleParameterSet("x = 2\ny = 3")
        self.assertRaises(KeyError, P.__getitem__, "z")

    def test__pretty__should_put_quotes_around_string_parameters(self):
        init = 'y = "hello"'
        P = SimpleParameterSet(init)
        self.assertEqual(P.pretty(), init)

    def test__pretty__should_recreate_comments_in_the_initializer(self):
        init = 'x = 2 # this is a comment'
        P = SimpleParameterSet(init)
        self.assertEqual(P.pretty(), init)

    def test__pretty__output_should_be_useable_to_create_an_identical_parameterset(self):
        init = "x = 2\ny = 3\nz = 'hello'"
        P1 = SimpleParameterSet(init)
        P2 = SimpleParameterSet(P1.pretty())
        self.assertEqual(P1.values, P2.values)

    def test__save__should_backup_an_existing_file_before_overwriting_it(self):
        # not really sure what the desired behaviour is here
        assert not os.path.exists("test_file.orig")
        init = "x = 2\ny = 3"
        with open("test_file", "w") as f:
            f.write(init)
        P = SimpleParameterSet("test_file")
        P.save("test_file")
        self.assert_(os.path.exists("test_file.orig"))
        os.remove("test_file")
        os.remove("test_file.orig")

    def test__update__should_only_accept_numbers_or_strings(self):
        # could maybe allow lists of numbers or strings
        P = SimpleParameterSet("x = 2\ny = 3")
        P.update({"z": "hello"})
        self.assertEqual(P["z"], "hello")
        P.update({"tumoltuae": 42})
        self.assertEqual(P["tumoltuae"], 42)
        self.assertRaises(TypeError, P.update, "bar", {})

    def test__str(self):
        P = SimpleParameterSet("x = 2\ny = 3")
        as_string = str(P)
        self.assertIsInstance(as_string, basestring)
        self.assertEqual(P, SimpleParameterSet(as_string))
    
    def test__pop(self):
        P = SimpleParameterSet("x = 2\ny = 3")
        self.assertEqual(P.pop('x'), 2)
        self.assertEqual(P.as_dict(), {'y': 3})


class TestConfigParserParameterSet(unittest.TestCase):
    test_parameters = dedent("""
        # this is a comment

        [sectionA]
        a: 2
        b: 3

        [sectionB]
        c: hello
        d: world
        """)

    def test__init__should_accept_an_empty_initializer(self):
        P = ConfigParserParameterSet("")
        self.assertEqual(P.as_dict(), {})

    def test__init__should_accept_a_filename_or_string(self):
        init = self.__class__.test_parameters
        P1 = ConfigParserParameterSet(init)
        with open("test_file", "w") as f:
            f.write(init)
        P2 = ConfigParserParameterSet("test_file")
        self.assertEqual(P1.as_dict(), P2.as_dict())
        os.remove("test_file")

    def test__pretty__output_should_be_useable_to_create_an_identical_parameterset(self):
        init = self.__class__.test_parameters
        P1 = ConfigParserParameterSet(init)
        P2 = ConfigParserParameterSet(P1.pretty())
        self.assertEqual(P1.as_dict(), P2.as_dict())

    def test__update_should_handle_dots_appropriately(self):
        init = self.__class__.test_parameters
        P = ConfigParserParameterSet(init)
        P.update({"sectionA.a": 5, "sectionA.c": 4, "sectionC.e": 9})
        self.assertEqual(P.as_dict(), {"sectionA": dict(a="5", b="3", c="4"),
                                       "sectionB": dict(c="hello", d="world"),
                                       "sectionC": dict(e="9")})

    def test__deepcopy(self):
        # see ticket:93
        init = self.__class__.test_parameters
        P = ConfigParserParameterSet(init)
        Q = deepcopy(P)

    def test__str(self):
        init = self.__class__.test_parameters
        P = ConfigParserParameterSet(init)
        as_string = str(P)
        self.assertIsInstance(as_string, basestring)
        self.assertEqual(P, ConfigParserParameterSet(as_string))
    
    def test__pop(self):
        init = self.__class__.test_parameters
        P = ConfigParserParameterSet(init)
        self.assertEqual(P.pop('sectionA.b'), '3')

    def test__getitem(self):
        init = self.__class__.test_parameters
        P = ConfigParserParameterSet(init)
        self.assertEqual(P['sectionA'], {'a': '2', 'b': '3'})
        self.assertEqual(P['sectionB.c'], 'hello')

class TestJSONParameterSet(unittest.TestCase):
    test_parameters = dedent("""
        {
            "a" : 2,
            "b" : "hello",
            "c" : {"a":1, "b":2},
            "d" : [1, 2, 3, 4]
        }
        """)

    def test__init__should_accept_an_empty_initializer(self):
        P = JSONParameterSet("")
        self.assertEqual(P.as_dict(), {})

    def test__init__should_accept_a_filename_or_string(self):
        init = self.__class__.test_parameters
        P1 = JSONParameterSet(init)
        with open("test_file", "w") as f:
            f.write(init)
        P2 = JSONParameterSet("test_file")
        self.assertEqual(P1.as_dict(), P2.as_dict())
        os.remove("test_file")

    def test_save(self):
        init = self.__class__.test_parameters
        P1 = JSONParameterSet(init)
        P1.save("test_file")
        P2 = JSONParameterSet("test_file")
        self.assertEqual(P1.as_dict(), P2.as_dict())
        os.remove("test_file")

    def test__pretty__output_should_be_useable_to_create_an_identical_parameterset(self):
        init = self.__class__.test_parameters
        P1 = JSONParameterSet(init)
        P2 = JSONParameterSet(P1.pretty())
        self.assertEqual(P1.as_dict(), P2.as_dict())

    def test__str(self):
        init = self.__class__.test_parameters
        P = JSONParameterSet(init)
        as_string = str(P)
        self.assertIsInstance(as_string, basestring)
    
    def test__pop(self):
        init = self.__class__.test_parameters
        P = JSONParameterSet(init)
        self.assertEqual(P.pop('a'), 2)
        self.assertEqual(P.pop('c'), {"a":1, "b":2})
        self.assertEqual(P.as_dict(), {'b': "hello", "d" : [1, 2, 3, 4]})


class TestYAMLParameterSet(unittest.TestCase):
    test_parameters = dedent("""
            a:   2
            b:   "hello"
            c:
              a: 1
              b: 2
            d:   [1, 2, 3, 4]
        """)

    @unittest.skipUnless(yaml_loaded, "PyYAML not available")
    def setUp(self):
        pass

    def test__init__should_accept_an_empty_initializer(self):
        P = YAMLParameterSet("")
        self.assertEqual(P.as_dict(), {})

    def test__init__should_accept_a_filename_or_string(self):
        init = self.__class__.test_parameters
        P1 = YAMLParameterSet(init)
        with open("test_file", "w") as f:
            f.write(init)
        P2 = YAMLParameterSet("test_file")
        self.assertEqual(P1.as_dict(), P2.as_dict())
        os.remove("test_file")

    def test_save(self):
        init = self.__class__.test_parameters
        P1 = YAMLParameterSet(init)
        P1.save("test_file")
        P2 = YAMLParameterSet("test_file")
        self.assertEqual(P1.as_dict(), P2.as_dict())
        os.remove("test_file")

    def test__pretty__output_should_be_useable_to_create_an_identical_parameterset(self):
        init = self.__class__.test_parameters
        P1 = YAMLParameterSet(init)
        P2 = YAMLParameterSet(P1.pretty())
        self.assertEqual(P1.as_dict(), P2.as_dict())

    def test__as_dict(self):
        init = self.__class__.test_parameters
        P = YAMLParameterSet(init)
        self.assertEqual(P.as_dict(),
                         {
                            "a" : 2,
                            "b" : "hello",
                            "c" : {"a":1, "b":2},
                            "d" : [1, 2, 3, 4]
                        })

    def test__str(self):
        init = self.__class__.test_parameters
        P = YAMLParameterSet(init)
        as_string = str(P)
        self.assertIsInstance(as_string, basestring)
    
    def test__pop(self):
        init = self.__class__.test_parameters
        P = YAMLParameterSet(init)
        self.assertEqual(P.pop('a'), 2)
        self.assertEqual(P.pop('c'), {"a":1, "b":2})
        self.assertEqual(P.as_dict(), {'b': "hello", "d" : [1, 2, 3, 4]})


class TestModuleFunctions(unittest.TestCase):

    def setUp(self):
        init = "x = 2\ny = 3"
        with open("test_file.simple", "w") as f:
            f.write(init)
        init2 = '{\n  "x": 2,\n  "y": {"a": 3, "b": 4}\n}'
        with open("test_file.hierarchical", "w") as f:
            f.write(init2)
        init3 = "[sectionA]\na = 2\nb = 3\n[sectionB]\nc = hello\nd = world"
        with open("test_file.config", "w") as f:
            f.write(init3)

    def tearDown(self):
        os.remove("test_file.simple")
        os.remove("test_file.hierarchical")
        os.remove("test_file.config")

    def test__build_parameters_simple(self):
        P = build_parameters("test_file.simple")
        self.assertEqual(P.as_dict(), {'x': 2, 'y': 3})
        self.assertIsInstance(P, SimpleParameterSet)
        
    def test__build_parameters_hierarchical(self):
        P = build_parameters("test_file.hierarchical")
        self.assertEqual(P.as_dict(), {'x': 2, 'y': {'a': 3, 'b': 4}})
        self.assertIsInstance(P, (JSONParameterSet, YAMLParameterSet, NTParameterSet))
    
    def test__build_parameters_config(self):
        P = build_parameters("test_file.config")
        self.assertEqual(P.as_dict(), {'sectionA': {'a': '2', 'b': '3'}, 'sectionB': {'c': 'hello', 'd': 'world'}})
        self.assertIsInstance(P, ConfigParserParameterSet)

    

# these tests should now be applied to commands.parse_arguments and/or commands.parse_command_line_parameter()
    #def test__build_parameters__should_add_new_command_line_parameters_to_the_file_parameters(self):
    #    P = build_parameters("test_file", ["z=42", "foo=bar"])
    #    self.assertEqual(P.values, {"x": 2, "y": 3, "z": 42, "foo": "bar"})
    #    P = build_parameters("test_file3", ["sectionA.c=42", "sectionC.foo=bar"])
    #    self.assertEqual(P["sectionA.c"], "42")
    #    self.assertEqual(P["sectionC.foo"], "bar")
    #
    #def test__build_parameters__should_overwrite_file_parameters_if_command_line_parameters_have_the_same_name(self):
    #    P = build_parameters("test_file", ["x=12", "y=13"])
    #    self.assertEqual(P.values, {"x": 12, "y": 13})
    #    P = build_parameters("test_file3", ["sectionA.a=999"])
    #    self.assertEqual(P["sectionA.a"], "999")
    #
    #def test__build_parameters__should_insert_dotted_parameters_in_the_appropriate_place_in_the_hierarchy(self):
    #    P = build_parameters("test_file2", ["z=100", "y.c=5", "y.a=-2"])
    #    assert isinstance(P, NTParameterSet), type(P)
    #    self.assertEqual(P.as_dict(), {
    #                                    "y": {
    #                                        "a": -2,
    #                                        "b": 4,
    #                                        "c": 5,
    #                                    },
    #                                    "x": 2,
    #                                    "z": 100,
    #                                  })
    #
    #
    #def test__build_parameters__should_cast_string_representations_of_numbers_within_lists_to_numeric_type(self):
    #    # unless they are in quotes
    #    # also applies to tuples
    #    # what about dicts or sets?
    #    P = build_parameters("test_file", ["M=[1,2,3,4,5]", "N=['1', '2', 3, 4, '5']"])
    #    self.assertEqual(P.values, {"x": 2, "y": 3, "M": [1,2,3,4,5], "N": ['1', '2', 3, 4, '5']})



if __name__ == '__main__':
    unittest.main()
