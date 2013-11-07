from __future__ import division

import matplotlib.pyplot as mp
import numpy as np
from scipy.constants import c, pi

from pyoperators import MaskOperator
from pysimulators import create_fitsheader, DiscreteSurface
from qubic import QubicInstrument

NU = 150e9                   # [Hz]
LAMBDA = c / NU              # [m]
FOCAL_LENGTH = 0.3           # [m]

SOURCE_POWER = 1             # [W]
SOURCE_THETA = np.radians(0) # [rad]
SOURCE_PHI = np.radians(45)  # [rad]

PRIMARY_BEAM_FWHM = 14       # [degrees]
SECONDARY_BEAM_FWHM = 14     # [degrees]

NHORN = 20**2
HORN_THICKNESS = 0.001       # [m]
HORN_KAPPA = 1.344
HORN_OPEN = np.zeros(2 * (np.sqrt(NHORN),), dtype=bool)
HORN_OPEN[10,10] = True
HORN_OPEN[11,11] = True
HORN_OPEN[0,1] = True
HORN_OPEN[17,18] = True
HORN_OPEN = np.ones(2 * (np.sqrt(NHORN),), dtype=bool)

NPOINT_DETECTOR_PLANE = 512**2 # number of detector plane sampling points
DETECTOR_PLANE_LIMITS = (-0.051, 0.051) # [m]

# to check energy conservation (unrealistic detector plane):
#DETECTOR_PLANE_LIMITS = (-4, 4) # [m]


#########
# SOURCE
#########
def ang2vec(theta_rad, phi_rad):
    sintheta = np.sin(theta_rad)
    return np.array([sintheta * np.cos(phi_rad),
                     sintheta * np.sin(phi_rad),
                     np.cos(theta_rad)])
source_uvec = ang2vec(SOURCE_THETA, SOURCE_PHI)
source_E = np.sqrt(SOURCE_POWER)


########
# BEAMS
########
class Beam(object):
    def __init__(self, fwhm_deg):
        self.sigma_deg = fwhm_deg / np.sqrt(8 * np.log(2))
        self.sigma_rad = np.radians(self.sigma_deg)
        self.fwhm_deg = fwhm_deg
        self.sr = 2 * pi * self.sigma_rad**2
class PrimaryBeam(Beam):
    def __call__(self, theta_rad):
        return np.exp(-theta_rad**2 / (2 * self.sigma_rad**2))
class SecondaryBeam(Beam):
    def __call__(self, theta_rad):
        return np.exp(-(pi - theta_rad)**2 / (2 * self.sigma_rad**2))
class UniformHalfSpaceBeam(object):
    def __init__(self):
        self.sr = 2 * pi
    def __call__(self, theta_rad):
        return 1
primary_beam = PrimaryBeam(PRIMARY_BEAM_FWHM)
secondary_beam = SecondaryBeam(SECONDARY_BEAM_FWHM)
#secondary_beam = UniformHalfSpaceBeam()


########
# HORNS
########
nhorn_x = int(np.sqrt(NHORN))
if nhorn_x**2 != NHORN:
    raise ValueError('Non-square arrays are not handled.')
nhorn_open = np.sum(HORN_OPEN)
horn_surface = HORN_KAPPA**2 * LAMBDA**2 / primary_beam.sr
horn_radius = np.sqrt(horn_surface / pi) + HORN_THICKNESS
horn_size_tot = 2 * horn_radius * nhorn_x
a = -horn_size_tot * 0.5 + horn_radius + horn_size_tot * np.arange(nhorn_x) / nhorn_x
horn_x, horn_y = np.meshgrid(a, a)
horn_vec = np.column_stack([horn_x[HORN_OPEN], horn_y[HORN_OPEN],
                            np.zeros(nhorn_open)])


#################
# DETECTOR PLANE
#################
def norm(x):
    return x / np.sqrt(np.sum(x**2, axis=-1))[..., None]
ndet_x = int(np.sqrt(NPOINT_DETECTOR_PLANE))
a = np.r_[DETECTOR_PLANE_LIMITS[0]:DETECTOR_PLANE_LIMITS[1]:ndet_x*1j]
det_x, det_y = np.meshgrid(a, a)
det_spacing = (DETECTOR_PLANE_LIMITS[1] - DETECTOR_PLANE_LIMITS[0]) / ndet_x
det_vec = np.dstack([det_x, det_y, np.zeros_like(det_x) - FOCAL_LENGTH])
det_uvec = norm(det_vec)
det_theta = np.arccos(det_uvec[...,2])

# solid angle of a detector plane pixel (gnomonic projection)
central_pixel_sr = np.arctan(det_spacing / FOCAL_LENGTH)**2
detector_plane_pixel_sr = -central_pixel_sr * np.cos(det_theta)**3


############
# DETECTORS
############
qubic = QubicInstrument('monochromatic,nopol')
header = create_fitsheader((ndet_x, ndet_x), cdelt=det_spacing, crval=(0, 0),
                           ctype=['X---CAR', 'Y---CAR'], cunit=['m', 'm'])
detector_plane = DiscreteSurface.fromfits(header)
integ = MaskOperator(qubic.detector.removed) * \
        detector_plane.get_integration_operator(qubic.detector.vertex)


########
# MODEL
########
E = np.sum(source_E *
           np.sqrt(primary_beam(SOURCE_THETA)) *
           np.sqrt(secondary_beam(det_theta) /
                   secondary_beam.sr *
                   detector_plane_pixel_sr)[..., None] *
           np.exp(2j * pi / LAMBDA * (np.dot(det_uvec, horn_vec.T) +
                                      np.dot(horn_vec, source_uvec))),
           axis=-1)
I = np.abs(E)**2
D = integ(I)


##########
# DISPLAY
##########
mp.figure()
mp.imshow(D, interpolation='nearest')
mp.gca().format_coord = lambda x,y: 'x={} y={} z={}'.format(x, y, D[x,y])
mp.show()
print('Given {} horns, we get {} W in the detector plane and {} W in the detec'
      'tors.'.format(nhorn_open, np.sum(I), np.sum(D)))
