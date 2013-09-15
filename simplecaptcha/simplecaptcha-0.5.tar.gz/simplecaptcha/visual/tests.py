""" Captcha.Visual.Tests

Visual CAPTCHA tests

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""
from simplecaptcha.visual import text, backgrounds, distortions, ImageCaptcha
from simplecaptcha import words
import random

__all__ = ["PseudoGimpy", "AngryGimpy", "AntiSpam"]


class PseudoGimpy(ImageCaptcha):
    """A relatively easy CAPTCHA that's somewhat easy on the eyes"""

    def get_layers(self):
        word = words.default_word_list.pick()
        self.add_solution(word)
        return [
            random.choice([
                backgrounds.CroppedImage(),
                backgrounds.TiledImage(),
            ]),
            text.TextLayer(word, border_size=1),
            distortions.SineWarp(),
            ]


class AngryGimpy(ImageCaptcha):
    """A harder but less visually pleasing CAPTCHA"""
    def get_layers(self):

        word = words.default_word_list.pick()
        self.add_solution(word)
        return [
            backgrounds.TiledImage(),
            backgrounds.RandomDots(),
            text.TextLayer(word, border_size=1),
            distortions.WigglyBlocks(),
            ]


class AntiSpam(ImageCaptcha):
    """A fixed-solution CAPTCHA that can be used to hide email addresses or
    URLs from bots"""

    font_factory = text.FontFactory(20, "vera/VeraBd.ttf")
    default_size = (512,50)

    def get_layers(self, solution="murray@example.com"):
        self.add_solution(solution)

        text_layer = text.TextLayer(solution,
                                   border_size=2,
                                   font_factory=self.font_factory)

        return [
            backgrounds.CroppedImage(),
            text_layer,
            distortions.SineWarp(amplitude_range=(2, 4)),
            ]
