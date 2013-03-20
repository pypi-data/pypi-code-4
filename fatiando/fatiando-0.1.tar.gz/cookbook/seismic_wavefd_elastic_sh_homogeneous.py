"""
Seismic: 2D finite difference simulation of elastic SH wave propagation in a
homogeneous medium (no Love wave)
"""
import numpy as np
from matplotlib import animation
from fatiando import seismic, logger, gridder, vis

log = logger.get()

# Make a wave source from a mexican hat wavelet
sources = [seismic.wavefd.MexHatSource(4, 20, 100, 0.5, delay=1.5),
           seismic.wavefd.MexHatSource(6, 22, 100, 0.5, delay=1.75),
           seismic.wavefd.MexHatSource(8, 24, 100, 0.5, delay=2)]
# Set the parameters of the finite difference grid
shape = (80, 400)
spacing = (1000, 1000)
area = (0, spacing[1]*shape[1], 0, spacing[0]*shape[0])
# Make a density and S wave velocity homogeneous model
dens = 2700*np.ones(shape)
svel = 3000*np.ones(shape)

# Get the iterator. This part only generates an iterator object. The actual
# computations take place at each iteration in the for loop bellow
dt = 0.05
maxit = 2400
timesteps = seismic.wavefd.elastic_sh(spacing, shape, svel, dens, dt, maxit,
    sources, padding=0.8)

# This part makes an animation using matplotlibs animation API
rec = 300 # The grid node used to record the seismogram
vmin, vmax = -3*10**(-4), 3*10**(-4)
fig = vis.mpl.figure(figsize=(10,6))
vis.mpl.subplots_adjust(left=0.1, right=0.98)
vis.mpl.subplot(2, 1, 2)
vis.mpl.axis('scaled')
x, z = gridder.regular(area, shape)
wavefield = vis.mpl.pcolor(x, z, np.zeros(shape).ravel(), shape,
    vmin=vmin, vmax=vmax)
vis.mpl.plot([rec*spacing[1]], [2000], '^b')
vis.mpl.ylim(area[-1], area[-2])
vis.mpl.m2km()
vis.mpl.xlabel("x (km)")
vis.mpl.ylabel("z (km)")
vis.mpl.subplot(2, 1, 1)
seismogram, = vis.mpl.plot([], [], '-k')
vis.mpl.xlim(0, dt*maxit)
vis.mpl.ylim(vmin*10.**(6), vmax*10.**(6))
vis.mpl.xlabel("Time (s)")
vis.mpl.ylabel("Amplitude ($\mu$m)")
times = []
addtime = times.append
amps = []
addamp = amps.append
# This function updates the plot every few timesteps
steps_per_frame = 100
#steps_per_frame = 1
def animate(i):
    # i is the number of the animation frame
    for t, u in enumerate(timesteps):
        addamp(10.**(6)*u[0, rec])
        addtime(dt*(t + i*steps_per_frame))
        if t == steps_per_frame - 1:
            break
    vis.mpl.title('time: %0.1f s' % (i*steps_per_frame*dt))
    seismogram.set_data(times, amps)
    wavefield.set_array(u[0:-1,0:-1].ravel())
    return seismogram, wavefield
anim = animation.FuncAnimation(fig, animate, frames=maxit/steps_per_frame,
    interval=1, blit=False)
#anim.save('sh_wave.mp4', fps=100)
vis.mpl.show()
