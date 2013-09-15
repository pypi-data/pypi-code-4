import unittest
from PIL import Image
from simplecaptcha.words import *
from simplecaptcha.visual.text import *
from simplecaptcha.visual.distortions import *
from simplecaptcha.visual.backgrounds import *
from simplecaptcha.visual.tests import *

class TestCaptcha(unittest.TestCase):
    """ Testing an actual full image render """

    def test_simple(self):
        for cls in [PseudoGimpy, AngryGimpy, AntiSpam]:
            s = cls()
            assert len(s.get_layers()) > 1
            assert s.get_image().size[0] >= 256

class TestWords(unittest.TestCase):
    """ Basic testing for the wordlist """

    def test_english(self):
        for i in range(0, 100):
            assert len(basic_english.pick()) > 0

    def test_restricted(self):
        for i in range(0, 100):
            l = len(basic_english_restricted.pick())
            assert l >= 5
            assert l <= 8

class TestText(unittest.TestCase):
    """ Surface level tests for the Font/Text management """

    def test_factory(self):
        for i in range(0, 100):
            p = default_font_factory.pick()
            assert type(p[1]) == int
            assert type(p[0]) == str

        assert default_font_factory.min_size > 0
        assert default_font_factory.max_size < 200

    def test_text_layer(self):
        text = TextLayer("tootle")

        assert len(text.font) > 1
        assert type(text.alignment) is tuple
        img = Image.new("RGB", (256, 96))
        text.render(img)

class TestDistortions(unittest.TestCase):
    """ Surface level tests for the Font/Text management """

    def test_all_basic(self):
        for cls in [WigglyBlocks, WarpBase, SineWarp]:
            t = cls()
            img = Image.new("RGB", (256, 96))
            t.render(img)

class TestBackgrounds(unittest.TestCase):
    """ Surface level tests for the Font/Text management """

    def test_all_basic(self):
        for cls in [RandomDots, CroppedImage, TiledImage, Grid, SolidColor]:
            t = cls()
            img = Image.new("RGB", (256, 96))
            t.render(img)

