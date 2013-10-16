#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   Alisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# Date:     2013-10-04
#
# (C) 2013 hashnote.net, Alisue
#
from functools import wraps
from functools import update_wrapper
import matplotlib.pyplot as pl
from graf.styles.color import color_cycle

"""matplotlib.pyplot commands which will be treated as command"""
_pyplot_commands = [
    'title', 'suptitle', 'grid',
    'xlabel', 'xticks', 'xlim', 'twinx',
    'ylabel', 'yticks', 'ylim', 'twiny',
    'tick_params', 'axes',
    'show', 'savefig',
    'text', 'box',
]
"""matplotlib.pyplot PLOT commands which will be treated as command"""
_pyplot_plot_commands = [
    'plot', 'errorbar', 'bar', 'axhline', 'axvline',
]


def original_color_cycle(fn):
    """
    A decorator to force using own color_cycle instead of matplotlib
    color_cycle. All method related to plotting should be wrapped with this
    decorator
    """
    def wrapper(*args, **kwargs):
        if kwargs.get('color', None) is None:
            kwargs['color'] = next(color_cycle)
        return fn(*args, **kwargs)
    return update_wrapper(wrapper, fn)

@wraps(pl.figure)
def figure(*args, **kwargs):
    # reset color cycle
    color_cycle.reset()
    return pl.figure(*args, **kwargs)

@wraps(pl.subplot)
def subplot(*args, **kwargs):
    # reset color cycle
    color_cycle.reset()
    return pl.subplot(*args, **kwargs)

@wraps(pl.legend)
def legend(*args, **kwargs):
    if len(args) == 0:
        # automatically create handles and labels from
        # all axes in the current figure
        handles = []
        labels = []
        fig = pl.gcf()
        for ax in fig.axes:
            _handles, _labels = ax.get_legend_handles_labels()
            handles += _handles
            labels += _labels
        args = [handles, labels]
    return pl.legend(*args, **kwargs)

# Create an plugin registry for loader class
def __plugin__(registry):
    # register alternative commands
    registry.register('figure', figure)
    registry.register('subplot', subplot)
    registry.register('legend', legend)
    # register commands
    for name in _pyplot_commands:
        fn = getattr(pl, name)
        registry.register(name, fn)
    # register commands related to plotting
    for name in _pyplot_plot_commands:
        fn = getattr(pl, name)
        registry.register(name, original_color_cycle(fn))
__plugin__.manually = True
