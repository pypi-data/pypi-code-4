import math

from pyrf.devices.thinkrf import WSA4000
from pyrf.util import read_data_and_reflevel
import numpy as np
import scipy.io as sio

# retrieve device id
hann_file = open("hann.txt", "w")
fft_raw_file = open("fft_raw.txt", "w")

np.set_printoptions(threshold=np.nan)

mat = sio.loadmat('raw_iq.mat')

i_data = (mat['iData'])
i_data.shape = (-1,)
q_data = (mat['qData'])
q_data.shape = (-1,)

han_window = np.hanning(len(i_data))
fft_raw = np.fft.fft(i_data + 1j * q_data)

hann_file.write(str(han_window))
fft_raw_file.write(str(fft_raw))




