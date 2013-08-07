import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_enum('bandgap', '0', ['0','50', '60'],
                   "Apply a sinc based bandgap filter to remove existing hum data at 50hz or 60hz.   Defaults to 0 which disables bandgap filtering")

gflags.DEFINE_string('start', None, "A human readable date and time indicating the start of the hum data.   This date must be between the start of dagrid.uis's data and now minus the length of the file (i.e. if your wav file is an hour long, start must be at least an hour ago")

gflags.DEFINE_boolean('reject_missing_data', False, "dagrid.us's hum data has holes where samples were rejected due to hardware failure.  Normally humbug_forensics will interpolate across missing sections.  Setting reject_missing_data to true will exit with an error code of 1 in the event of incomplete data.  Using this flag does NOT ensure the data is correct.  Dagrid.us's hardware is pretty nasty.")

gflags.DEFINE_float('intensity', 1.0, 'The amplitude of the A/C signal to inject.  The unit here is "sample value", so the actual amplitude will vary depending on wav file precision.    humbug forensics supports subsample dithering.')



import dateutil.parser
import math
import sys
import requests
from datetime import datetime, timedelta
import pysox
from fractions import Fraction

def parse_date(s):
    return dateutil.parser.parse(s)

def parse_data(s):
    for line in s.split('\n'):
        line = line.strip()
        if not line: continue
        
        line = line.replace('"', '')
        timestamp, freq = line.split(',')
        freq = freq.split('h')[0]

        day, hour = timestamp.split(' ')
        year, month, day = day.split('/')
        hour, minute = hour.split(':')
        yield datetime(year=int(year), 
                       month=int(month), 
                       day=int(day),
                       hour=int(hour), 
                       minute=int(minute), 
                       second=0), float(freq)

class Humbugger(pysox.CCustomEffect):
    def __init__(self, start, data, siginfo):
        pysox.CCustomEffect.__init__(self, 'hambugger', [])
        self.__start = start
        self.__data = list(reversed(data))
        self.__channels = siginfo['channels']
        self.__rate = Fraction(1, int(siginfo['rate']))
        self.__samplerate = float(siginfo['rate'])
        self.__sample = 0 
        self.__sprev = 1/60.0
        self.__sprev2 = 0
        self.__siginfo = siginfo
        self.__mult = 2**(31 - self.__siginfo['precision'])
        

    def now(self):
        return self.__start + timedelta(seconds=float(self.__rate * self.__sample))

    def freq(self):
        t = self.now()
        while t > self.__data[-2][0]:
            print "Next sample"
            self.__data.pop()
        t0, f0 = self.__data[-1]
        t1, f1 = self.__data[-2]

        t0 = abs((t0 - t).total_seconds())
        t1 = abs((t1 - t).total_seconds())
        self.__sample += 1 
        return (t0  f0 + t1 * f1) / (t0 + t1)
        

    def flow(self, inbuf, outbuf, samples):
        if not samples: return 0
        l = inbuf.tolist()
        offset = 0
        intensity = FLAGS.intensity * self.__mult
        for x in range(samples / self.__channels):
            f = self.freq()
            coeff =  2 * math.cos(2*3.141592653589 * f / self.__samplerate)
            s =  coeff * self.__sprev - self.__sprev2
            self.__sprev2 = self.__sprev
            self.__sprev = s
            for y in range(self.__channels):
                l[offset] += s * intensity
                offset += 1
            
        outbuf.writelist(map(int, l))
        return samples

    def stop(self):
        return 0

def main(argv=None, stdin=None, stdout=None, stderr=None):
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr 

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s <infile> <oufile>\\n%s\n" % (
                e, sys.argv[0], FLAGS))

    if len(argv) != 2:
        stderr.write("Usage: %s <infile> <oufile>\\n%s\n" % (
                sys.argv[0], FLAGS))
        
    infile, outfile = argv
    start = parse_date(FLAGS.start)

    data = requests.get("http://dagrid.us/alldata.csv").text
    data = parse_data(data)
    data = [d for d in data if d[0] >= start - timedelta(minutes=1)]

    in_wav = pysox.CSoxStream(infile)
    out_wav = pysox.CSoxStream(outfile, "w", in_wav.get_signal())
    chain = pysox.CEffectsChain(in_wav, out_wav)
    if FLAGS.bandgap == '50':
        chain.add_effect(pysox.CEffect("sinc",[b'49.8', b'50.2']))
    elif FLAGS.bandgap == '60':
        chain.add_effect(pysox.CEffect("sinc",[b'59.8', b'60.2']))
    
    if FLAGS.intensity != '0':
        chain.add_effect(Humbugger(start, data, in_wav.get_signal().get_signalinfo()))
    chain.flow_effects()
    out_wav.close()

