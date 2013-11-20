import unittest

from stxnext.grayscale import utils


HEX_COLORS = """
border: 1px solid #fff;
border: 1pt solid #00FF00;
background: 123456;
background:#aaaaaa;
color:#1234;

style="color:#ff0"
"""
HEX_MATCH = sorted(['#fff', '#00FF00', '#aaaaaa', '#ff0'])

RGB_RGBA_COLORS = """
border: 1px solid rgb(10%, 20%, 10%);
border: 1pt solid rgba(11%,22%,33%, 0.1);
background: rgb(11,11);
background:rgba(44,55,66, 1);
color:rgb(44%,55%,66%);

style="color: rgba(1,2,3)"
"""
RGB_RGBA_MATCH = sorted(['rgb(10%, 20%, 10%)', 'rgba(11%,22%,33%, 0.1)',
    'rgb(11,11)', 'rgba(44,55,66, 1)', 'rgb(44%,55%,66%)', 'rgba(1,2,3)'])

NAMED_COLORS = """
border: 1px solid white; // will not be matched
border: 1pt solid black; // will not be matched
background-color: 123456;
color:       yellow;

style="color:red"
"""
NAMED_MATCH = sorted(['color:       yellow', 'color:red'])


class TestRegexpPatterns(unittest.TestCase):
    """
    Tests for regexp patterns
    """
    def test_match_hex_colors(self):
        """
        Tests COLOR_PATTERN for hex colors
        """
        colors = sorted(utils.COLOR_PATTERN.findall(HEX_COLORS))
        self.assertEqual(colors, HEX_MATCH)

    def test_match_rgb_rgba_colors(self):
        """
        Tests COLOR_PATTERN for RGB and RGBA colors
        """
        colors = sorted(utils.COLOR_PATTERN.findall(RGB_RGBA_COLORS))
        self.assertEqual(colors, RGB_RGBA_MATCH)

    def test_match_named_colors(self):
        """
        Tests COLOR_PATTERN for colors specified by name
        """
        colors = sorted(utils.COLOR_PATTERN.findall(NAMED_COLORS))
        self.assertEqual(colors, NAMED_MATCH)

    def test_dont_match_entities(self):
        """
        Tests if COLOR_PATTERN will not match HTML entities
        """
        entities = "&#60; &#160 &#182; &#8364; &#123456"
        self.assertFalse(utils.COLOR_PATTERN.findall(entities))


class TestAddParamToUrl(unittest.TestCase):
    """
    Test for stxnext.grayscale.utils.add_param_to_url function
    """

    def test_add_param_to_domain_wo_params(self):
        url_domain_only = 'http://example.com'
        self.assertEqual(utils.add_param_to_url(url_domain_only),
                'http://example.com?grayscale=1')

    def test_add_param_to_path_wo_params(self):
        url_with_path = 'http://example.com/abc/efg/'
        self.assertEqual(utils.add_param_to_url(url_with_path),
                'http://example.com/abc/efg/?grayscale=1')

    def test_add_param_to_file_wo_params(self):
        url_with_file = 'http://example.com/file.html'
        self.assertEqual(utils.add_param_to_url(url_with_file),
                'http://example.com/file.html?grayscale=1')

    def test_add_param_to_domain_w_params(self):
        url_domain_only = 'http://example.com?param1=2'
        self.assertEqual(utils.add_param_to_url(url_domain_only),
                'http://example.com?param1=2&grayscale=1')

    def test_add_param_to_path_w_params(self):
        url_with_path = 'http://example.com/abc/efg/?param1=2'
        self.assertEqual(utils.add_param_to_url(url_with_path),
                'http://example.com/abc/efg/?param1=2&grayscale=1')

    def test_add_param_to_file_w_params(self):
        url_with_file = 'http://example.com/file.html?param1=2'
        self.assertEqual(utils.add_param_to_url(url_with_file),
                'http://example.com/file.html?param1=2&grayscale=1')


class TestTransformImgSrc(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.transform_img_src
    """
    def test_simple_img_tag(self):
        tag = """<img src="logo.png" />"""
        self.assertEqual(utils.transform_img_src(tag),
                """<img src="logo.png?grayscale=1" />""")

    def test_simple_img_tag_w_parmas(self):
        tag = """<img src="logo.png?param1=2" />"""
        self.assertEqual(utils.transform_img_src(tag),
                """<img src="logo.png?param1=2&grayscale=1" />""")

    def test_multiline_img_tag(self):
        tag = """<img
src="logo.png" />"""
        self.assertEqual(utils.transform_img_src(tag), """<img
src="logo.png?grayscale=1" />""")


class TestTransformCssUrl(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.transform_css_url
    """
    def test_simple_css_url(self):
        css = """background: url(background.png)"""
        self.assertEqual(utils.transform_css_url(css),
                """background: url(background.png?grayscale=1)""")

    def test_simple_css_url_w_param(self):
        css = """background: url(background.png?param1=2)"""
        self.assertEqual(utils.transform_css_url(css),
                """background: url(background.png?param1=2&grayscale=1)""")

    def test_simple_css_url_w_quotation(self):
        css = """background: url("background.png")"""
        self.assertEqual(utils.transform_css_url(css),
                """background: url("background.png?grayscale=1")""")

    def test_simple_css_w_apostrophe(self):
        css = """background: url('background.png')"""
        self.assertEqual(utils.transform_css_url(css),
                """background: url('background.png?grayscale=1')""")


class TestTransformValue(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.transform_value
    """
    def test_transform_named_color(self):
        """
        Test for standard named color
        """
        color = 'color: blue;'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, 'color: #1d1d1d')

    def test_transform_named_color_w_whitespaces(self):
        """
        Tests if named color with whitespaces will be transformed correctly
        """
        color = 'color:               gray        ;'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, 'color: #808080')

    def test_transform_other_named_color(self):
        """
        Tests if named color not included in utils.KWRD_MAP will be left unchanged
        """
        color = 'color: brown;'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, color)

    def test_transform_hex_6(self):
        """
        Tests if normal hex (6 chars) will be transformed correctly
        """
        color = '#ff0000'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, '#4c4c4c')

    def test_transform_hex_3(self):
        """
        Tests if normal hex (3 chars) will be transformed correctly
        """
        color = '#f00'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, '#4c4c4c')

    def test_transform_incorrect_len_hex(self):
        """
        Tests if hex with incorrect length will not be transformed
        """
        color = '#ff00'
        self.assertRaises(ValueError, utils.transform_value, color)

    def test_transform_incorrect_val_hex(self):
        """
        Tests if hex with incorrect values will not be transformed
        """
        color = '#qw0000'
        self.assertRaises(ValueError, utils.transform_value, color)

    def test_transform_rgb(self):
        """
        Tests rgb() color transformation
        """
        color = 'rgb(255, 0, 0)'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, '#4c4c4c')

    def test_transform_rgba(self):
        """
        Tests rgba() color transformation
        """
        color = 'rgba(255, 0, 0, 1)'
        transformed = utils.transform_value(color)
        self.assertEqual(transformed, 'rgba(76, 76, 76, 1.0)')


class TestGrayscaleTupe(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.grayscale_tuple
    """

    def test_empty_tuple(self):
        self.assertRaises(ValueError, utils.grayscale_tuple, [])

    def test_icorrect_len_tuple(self):
        self.assertRaises(ValueError, utils.grayscale_tuple, [1,2])

    def test_incorrect_val_tuple(self):
        self.assertRaises(ValueError, utils.grayscale_tuple, ['a', 'b', 'c'])

    def test_not_tuple_or_list(self):
        self.assertRaises(ValueError, utils.grayscale_tuple, 'string')

    def test_correct_input(self):
        color = (255, 0, 0)
        self.assertEqual(utils.grayscale_tuple(color), (76, 76, 76))


class TestHexToTuple(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.hex_to_tuple
    """

    def test_empty_text(self):
        self.assertRaises(ValueError, utils.hex_to_tuple, '')

    def test_incorrect_len_text(self):
        self.assertRaises(ValueError, utils.hex_to_tuple, '#a')

    def test_incorrect_val_text(self):
        self.assertRaises(ValueError, utils.hex_to_tuple, '#qwe')

    def test_correct_input_6(self):
        text = '#ff0000'
        self.assertEqual(utils.hex_to_tuple(text), (255, 0, 0))

    def test_correct_input_3(self):
        text = '#f00'
        self.assertEqual(utils.hex_to_tuple(text), (255, 0, 0))

    def test_input_w_whitespace(self):
        text = '             #ff0000             '
        self.assertEqual(utils.hex_to_tuple(text), (255, 0, 0))

    def test_input_wo_hash(self):
        text = 'ff0000'
        self.assertEqual(utils.hex_to_tuple(text), (255, 0, 0))


class TestRgbToTuple(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.rgb_to_tuple
    """

    def test_correct_numbers_input(self):
        text = 'rgb(1,2,3)'
        self.assertEqual(utils.rgb_to_tuple(text), (1, 2, 3))

    def test_correct_percentages_input(self):
        text = 'rgb(100%, 0, 0)'
        self.assertEqual(utils.rgb_to_tuple(text), (255, 0, 0))

    def test_not_rgb_input(self):
        text = 'some string'
        self.assertEqual(utils.rgb_to_tuple(text), ())


class TestRgbaGrayscake(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.rgba_grayscale
    """

    def test_incorrect_len_input(self):
        """
        Tests for situtation when (for example) rgb() will be passed
        """
        text = 'rgb(1, 2, 3)'
        self.assertRaises(ValueError, utils.rgba_grayscale, text)

    def test_input_w_float_alpha(self):
        text = 'rgba(255, 0, 0, 0.1)'
        self.assertEqual(utils.rgba_grayscale(text), 'rgba(76, 76, 76, 0.1)')

    def test_input_w_int_alpha(self):
        text = 'rgba(255, 0, 0, 1)'
        self.assertEqual(utils.rgba_grayscale(text), 'rgba(76, 76, 76, 1.0)')


class TestAddBodyclass(unittest.TestCase):
    """
    Tests for stxnext.grayscale.utils.add_bodyclass
    """

    def test_body_no_attrs(self):
        text = """<body>"""
        self.assertEqual(utils.add_bodyclass(text),
                """<body class="gray-style">""")

    def test_body_w_attrs(self):
        text = """<body dir="ltr">"""
        self.assertEqual(utils.add_bodyclass(text),
                """<body dir="ltr" class="gray-style">""")

    def test_body_w_class_no_other_attrs(self):
        text = """<body class='homepage'>"""
        self.assertEqual(utils.add_bodyclass(text),
                """<body class='gray-style homepage'>""")

    def test_body_w_class_many_no_other_attrs(self):
        text = """<body class="homepage template-document_view">"""
        self.assertEqual(utils.add_bodyclass(text),
                """<body class="gray-style homepage template-document_view">""")

    def test_body_w_class_w_other_attrs(self):
        text = """<body class='homepage template-document_view' dir='ltr'>"""
        self.assertEqual(utils.add_bodyclass(text),
                """<body class='gray-style homepage template-document_view' dir='ltr'>""")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
