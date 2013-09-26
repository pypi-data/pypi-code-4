#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from optparse import OptionParser
from hytrp.client import *
from hytrp.protocol import *

parser = OptionParser()
parser.add_option("-d", "--device", dest="device", metavar="FILE", help="tty device to communicate", default="/dev/ttyS0")
parser.add_option("-r", "--baudrate", dest="rate", metavar="RATE", help="baudrate for device", default=9600, type="int")
parser.add_option("-q", "--quite", dest="quite", default=False, help="don't print output", action="store_true")
parser.add_option("--reset", dest="reset", default=False, help="reset to factory defaults", action="store_true")
parser.add_option("--frequency", dest="frequency", metavar="FREQ", help="set working frequency, Hz", type="int")
parser.add_option("--power", dest="power", metavar="PWR", help="set working power, dBm", type="int")
parser.add_option("--newrate", dest="newrate", metavar="RATE", help="set new serial rate, bps", type="int")
parser.add_option("--wrate", dest="wrate", metavar="RATE", help="set wireless rate, bps", type="int")
parser.add_option("--bandwidth", dest="bandwidth", metavar="FREQ", help="set bandwidth, KHz", type="int")
parser.add_option("--deviation", dest="deviation", metavar="FREQ", help="set frequency deviation, KHz", type="int")

(options, args) = parser.parse_args()

c = Client(port = options.device, baudrate = options.rate, timeout = 5)
if options.reset:
    c(Reset())
if options.frequency:
    c(Frequency(frequency=options.frequency))
if options.power:
    c(Power(power=options.power))
if options.newrate:
    c(Rate(rate=options.newrate))
if options.wrate:
    c(WRate(wrate=options.wrate))
if options.bandwidth:
    c(Bandwidth(bandwidth=options.bandwidth))
if options.deviation:
    c(Deviation(deviation=options.deviation))

if not options.quite:
    fmt = """
Working frequency:   %d Hz
Wireless data rate:  %d bps
Receiving bandwidth: %d KHz
Frequency deviation: %d KHz
Transmission power:  %d dBm
Serial data rate:    %d bps
    """
    current = c(Config())
    print fmt % (current['frequency'], current['wrate'], current['bandwidth'], current['deviation'], current['power'], current['rate'])
