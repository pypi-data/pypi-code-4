#! /usr/bin/python
#
# Plot the coherence magnitude curve for the Sun
# See Born & Wolf, p. 576
#
# Ludwig Schwardt
# 31 January 2008
# Updated to HTML demo version on 13 July 2013
#

import numpy as np
try:
    # SciPy is an optional dependency to get the jinc function
    import scipy.special as sp
except ImportError:
    sp = None
import matplotlib
matplotlib.use('module://mplh5canvas.backend_h5canvas')
from pylab import *

# Angular diameter of the source, in arcminutes (default = Sun's diameter)
diam_arcmin = 32.0

# Frequency of waves, in GHz
freq = 1.822

# Speed of light, in m/s
c = 3e08

# Equivalent wavelength, in m
lamb = c / (freq * 1e9)

# Various baseline lengths, in m
b = np.arange(0, 250, 0.5)

if sp:
    def jinc(x):
        """Jinc function (J_1(x) / x)."""
        j = np.ones(x.shape)
        # Handle 0/0 at origin
        nonzero_x = abs(x) > 1e-20
        j[nonzero_x] = 2 * sp.j1(np.pi * x[nonzero_x]) / (np.pi * x[nonzero_x])
        return j
else:
    # Fall back to sinc in the absence of SciPy (why not for a demo?)
    jinc = np.sinc

def cohmag(b, diam_arcmin):
    """Coherence magnitude as a function of distance and angular diameter."""
    # Angular diameter in radians
    diam = diam_arcmin / 60.0 * np.pi / 180.0
    # Normalised distance, in wavelengths
    v = diam * b / lamb
    return abs(jinc(v))

# Create basic plot using sparse figure background
fig = figure(1, facecolor='w', frameon=False)
clf()
plot(b, cohmag(b, diam_arcmin))
xlabel('Baseline length (m)')
ylabel('Amplitude')
title('Fringe visibility amplitude at %5.3f GHz' % freq)

def user_event(figure_id, *args):
    """Handle JS user event: modification of source diameter via slider."""
    fig = figure(int(figure_id) + 1)
    ax = fig.axes[0]
    diameter = float(args[0])
    # Update plot data in-place, preserving static parts of plot
    ax.lines[0].set_ydata(cohmag(b, diameter))
    fig.canvas.draw()
# Register handler for client side javascript calls to user_event
fig.canvas._user_event = user_event

# Read in a custom HTML wrapper and populate dynamic content
html_wrap_file = open("./examples/slider_plot.html")
fig.canvas._custom_content = html_wrap_file.read()
html_wrap_file.close()

# Use a single-figure layout: browse to http://ip:port/figure1 to get to plot
show(layout='figure1')
