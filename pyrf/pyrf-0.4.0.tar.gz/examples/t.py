import numpy as np

in_arr = []
for iq in open('iq.txt'):
    i, q = (int(x) for x in iq.split(','))
    in_arr.append(i + 1j * q)

out_arr = np.fft.fft(in_arr)

for iq in out_arr:
    print '%s,%s' % (iq.real, iq.imag)


