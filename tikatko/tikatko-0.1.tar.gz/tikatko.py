#! /usr/bin/env python2
"""A lightning talk timer

Usage:
tikatko.py
tikatko.py MIN
tikatko.py MIN:SEC

Press ESC to exit once running
"""

from __future__ import division
import math
import sys

from gillcup import AnimatedProperty, Animation
from gillcup_graphics import Layer, Text, Rectangle, Window, RealtimeClock, run

TAU = math.pi / 2
DEFAULT_TIME = 5 * 60

class Countdown(Text):
    time = AnimatedProperty(DEFAULT_TIME)

    @property
    def text(self):
        text = "{0}:{1:02}".format(*divmod(int(abs(math.ceil(self.time))), 60))
        if self.time > -1:
            return text
        else:
            return '-{}'.format(text)
    @text.setter
    def text(self, new_text):
        pass


def main(time):
    top_layer = Layer(relative_anchor=(0.5, 0.5))
    clock = RealtimeClock()
    Window(top_layer, fullscreen=True)

    text_layer = Layer(top_layer,
        scale=(1, top_layer.scale_x/top_layer.scale_y))

    text = Countdown(text_layer, '', scale=0.001, font_size=256,
        relative_anchor=(0.5, 0.8), position=(0.5, 0.5), time=time)

    def game_over():
        def easing(power):
            return lambda x: 1 - (math.sin(x * TAU) / 2 + 0.5) ** power
        rect = Rectangle(top_layer, color=(1, 0, 0), opacity=0)
        clock.schedule(Animation(rect, 'color', 1, 1, 0,
            timing='infinite', easing=easing(1), time=0.1))
        clock.schedule(Animation(rect, 'opacity', 0.5, time=1))

    clock.schedule(Animation(text, 'time', 0, time=time, timing='infinite'))
    clock.schedule(game_over, dt=time)

    run()


def script_entry_point():
    if len(sys.argv) > 2 or any(a in ('-h', '--help') for a in sys.argv):
        print(__doc__)
        exit()
    try:
        timestring = sys.argv[1]
    except IndexError:
        time = DEFAULT_TIME
    else:
        if ':' not in timestring:
            timestring += ':'
        time = 0
        for part in timestring.split(':'):
            time *= 60
            if part:
                time += int(part)
    return main(time)


if __name__ == '__main__':
    script_entry_point()
