# ----------------------------------------
# Copyright (C) 2010-2012  Frank Paehlke
#
# This file is part of TourEditor.
#
# TourEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TourEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TourEditor.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------

import codecs
import datetime
import tourfilesmooth

try:
    import gpxdata
    _no_gpxdata = False
except ImportError:
    _no_gpxdata = True

def td2seconds (timedelta):
    return 86400 * timedelta.days + timedelta.seconds + timedelta.microseconds/1e6

# ----------------------------------------

class TourFile:
    "representation of a Tour file"
    
    # column names
    columns = ['time', 'distance', 'height', 'lat', 'lon', 'heart_rate', 'temperature',
               'smooth_time', 'smooth_distance', 'smooth_height', 'speed', 'vspeed', 'slope' ,'comment']

    # mapping from column name to column index
    _columnindex = dict([(columns[i], i) for i in range(len(columns))])
    
    def __init__ (self, title=None, date=None, copyright=None):
        self.points = []
        self.title = title
        self.date = date
        self.copyright = copyright
        self.dmin = None
        self.dmax = None
        self.hmin = None
        self.hmax = None
        self.smin = None
        self.smax = None
        self.filename = '<>'
        self.filetype= None
        self.encoding = None
        self.is_smoothed = False
        self.speed_is_original = True

    def __len__ (self):
        "return number of points"
        return len(self.points)
    
    def get (self, row, column=None):
        "get value of row-th point"
        if column == None:
            return self.points[row]
        else:
            return self.points[row][self._columnindex[column]]

    def getcolumn (self, column):
        "get all values of column"
        col = self._columnindex[column]
        return [p[col] for p in  self.points]

    def put (self, row, point=None, **kw):
        "set value(s) of row-th point"
        if point == None:
            for key, value in kw.items():
                if key == 'time':
                    value = datetime.datetime.strptime(value, '%H:%M:%S')
                elif key != 'commment':
                    value = float(value)
                self.points[row][self._columnindex[key]] = value
        elif len(point) != len(self.columns):
            raise Exception ("trying to insert point with wrong number of elements")
        else:
            self.points[row] = point

    def append (self, point=None, **kw):
        if point == None:
            # convert key/value list to point
            p = []
            for col in self.columns:
                if col in kw:
                    p.append (kw[col])
                else:
                    p.append (None)
            self.points.append (p)
        elif len(point) != len(self.columns):
            raise Exception ("trying to insert point with wrong number of elements")
        else:
            self.points.append (point)

    def delete (self, row):
        del self.points[row]

    def clear (self):
        self.points = []

    def distance (self, i, j):
        "distance between point i and j"
        col = self._columnindex['distance']
        return self.points[j][col] - self.points[i][col]

    def length (self):
        "return tour length [km]"
        if len(self.points) == 0:
            return 0.0
        else:
            col = self._columnindex['distance']
            return self.points[-1][col] - self.points[0][col]

    def hdiff (self, net=False):
        "return height difference [m]"
        if len(self.points) == 0:
            return 0.0
        else:
            col = self._columnindex['smooth_height' if self.is_smoothed else 'height']
            if net:
                return self.points[-1][col] - self.points[0][col]
            else:
                return sum([
                    self.points[i+1][col] - self.points[i][col]
                    for i in range(len(self.points)-1)
                    if self.points[i+1][col] > self.points[i][col]
                    ])

    def slope (self):
        "return average slope [%]"
        if len(self.points) == 0:
            return None
        else:
            return self.hdiff (True) / self.length () / 10.0
                
    def maxslope (self):
        "return maximum slope [%]"
        if len(self.points) == 0:
            return None
        else:
            col = self._columnindex['slope']
            return max ([ p[col] for p in self.points ])
                
    def reverse (self):
        "reverse tour direction"
        if len(self.points) == 0:
            return
        dcol = self._columnindex['distance']
        start = self.points[0][dcol]
        end = self.points[-1][dcol]
        points = []
        for i in range(len(self.points)-1, -1, -1):
            p = self.points[i]
            p[dcol] = start + end - p[dcol]
            points.append (p)
        self.points = points
        self.calc_vspeed()
        self.calc_slope()

    def heightOffset (self, offset, rows=None):
        """add offset to heights"""
        if rows == None:
            rows = range(len(self.points)) # select all rows
        hcol = self._columnindex['height']
        shcol = self._columnindex['smooth_height']
        for i in rows:
            p = self.points[i]
            p[hcol] += offset
            if p[shcol] != None:
                p[shcol] += offset
        # no need to recalculate distance/slope

    def distanceOffset (self, offset, rows=None):
        """add offset to heights"""
        if rows == None:
            rows = range(len(self.points)) # select all rows
        dcol = self._columnindex['distance']
        sdcol = self._columnindex['smooth_distance']
        for i in rows:
            p = self.points[i]
            p[dcol] = round(p[dcol] + offset, 3)
            if p[sdcol] != None:
                p[sdcol] += offset
        # no need to recalculate distance/slope

    def simplify (self, delta=1.0):
        latcol = self._columnindex['lat']
        loncol = self._columnindex['lon']
        seg = gpxdata.TrackSegment(
            [ gpxdata.TrackPoint(p[latcol], p[loncol])
              for p in self.points
              if p[latcol] != None and p[loncol] != None
              ]
            )
        n = len(seg.points)
        idx = [0] + seg._simplify (0, n-1, delta) + [n-1]
        self.points = [ self.points[i] for i in idx ]        
        self.recalc()

    def smooth (self, fixedRows=set(), tf=tourfilesmooth.TFLength,
                startHeight=None, endHeight=None):
        smooth = tourfilesmooth.TourFileSmooth (tf)
        dcol = self._columnindex['distance']
        hcol = self._columnindex['height']
        sdcol = self._columnindex['smooth_distance']
        shcol = self._columnindex['smooth_height']
        # call smoothing algorithm
        s, h = smooth.smooth (
            [p[dcol] for p in self.points],
            [p[hcol] for p in self.points],
            0.005, 0.5, fixed=fixedRows )
        if startHeight != None and endHeight != None:
            # scale height values
            h0 = h[0]
            h1 = h[-1]
            scale = (endHeight-startHeight) / (h1-h0)
            for i in range(len(h)):
                h[i] = startHeight + scale * (h[i]-h0)
        # write results to tourfile
        for i in range(len(self.points)):
            self.points[i][sdcol] = s[i]
            self.points[i][shcol] = h[i]
        self.is_smoothed = True
        self.recalc()

    def calc_speed (self):
        if self.speed_is_original or len(self.points) == 0:
            return
        tcol = self._columnindex['time']
        dcol = self._columnindex['smooth_distance' if self.is_smoothed else 'distance']
        scol = self._columnindex['speed']
        self.points[0][scol] = None
        for i in range(1, len(self.points)):
            curr = self.points[i]
            prev = self.points[i-1]
            if curr[tcol] == None or prev[tcol] == None:
                continue
            tdiff = td2seconds(curr[tcol] - prev[tcol]) / 3600.0
            distance = curr[dcol] - prev[dcol]
            if tdiff != 0:
                self.points[i][scol] = round (distance/tdiff, 2)

    def calc_vspeed (self):
        if len(self.points) == 0:
            return
        tcol = self._columnindex['time']
        hcol = self._columnindex['smooth_height' if self.is_smoothed else 'height']
        vscol = self._columnindex['vspeed']
        self.points[0][vscol] = None
        for i in range(1, len(self.points)):
            curr = self.points[i]
            prev = self.points[i-1]
            if curr[tcol] == None or prev[tcol] == None:
                continue
            tdiff = td2seconds(curr[tcol] - prev[tcol]) / 3600.0
            hdiff = curr[hcol] - prev[hcol]
            if tdiff != 0:
                self.points[i][vscol] = round (hdiff/tdiff)

    def calc_slope (self):
        if len(self.points) == 0:
            return
        dcol = self._columnindex['smooth_distance' if self.is_smoothed else 'distance']
        hcol = self._columnindex['smooth_height' if self.is_smoothed else 'height']
        slcol = self._columnindex['slope']
        self.points[0][slcol] = None
        for i in range(1, len(self.points)):
            curr = self.points[i]
            prev = self.points[i-1]
            distance = curr[dcol] - prev[dcol]
            hdiff = curr[hcol] - prev[hcol]
            if distance != 0:
                self.points[i][slcol] = round (hdiff/distance/10.0, 1)

    def recalc(self):
        self.calc_speed()
        self.calc_vspeed()
        self.calc_slope()

    @staticmethod
    def readCRP (infile, encoding='iso-8859-1'):
        if isinstance (infile, basestring):
            # infile is a file name
            fp = open (infile, "rb")
            try:
                res = TourFile.readCRP (fp)
            finally:
                fp.close()
            return res
        # infile is a file pointer
        res = TourFile()
        res.filename = infile.name
        res.filetype = 'CRP'
        res.encoding = encoding
        reader = codecs.getreader(encoding)(infile)
        line = reader.readline()
        if line.startswith("HRMProfil"):
            # input includes complete CRP header
            # we can safely ignore the 2nd header line since we do not need
            # any of the contained data
            line = reader.readline()
            # read first real input line into buffer
            line = reader.readline()
            if not line:
                return res
        while line:
            if line.startswith("***"):
                # end of data rows reached; the input seems to contain a
                # complete CRP trailer: read it
                # ignore first line
                line = reader.readline()
                if not line: return res
                # second line
                line = reader.readline()
                if not line: return res
                fields = line.rstrip().split("\t")
                res.date = datetime.datetime.strptime(fields[0]+" "+fields[1], "%d.%m.%Y %H:%M:%S")
                res.title = fields[5]
                # the rest of the file can be ignored
                return res
            # read normal data row
            fields = line.rstrip().split("\t")
            kw = {}
            kw['heart_rate'] = float(fields[0])
            kw['speed'] = float(fields[1]) / 10.0 # unit: km/h
            kw['distance'] = float(fields[2]) / 100.0 # unit: km
            kw['height'] = int(fields[3])
            kw['temperature'] = float(fields[6].replace(",","."))
            kw['time'] = datetime.datetime.strptime (fields[7], "%H:%M:%S")
            if len(fields) > 8: kw['comment'] = fields[8]
            res.append (**kw)
            line = reader.readline()
        res.is_smoothed = False
        res.speed_is_original = True
        res.recalc()
        return res

    @staticmethod
    def readCSV (infile, encoding='utf-8'):
        if isinstance (infile, basestring):
            # infile is a file name
            fp = open (infile, "rb")
            try:
                res = TourFile.readCSV (fp, encoding)
            finally:
                fp.close()
            return res
        # infile is a file object
        res = TourFile()
        res.filename = infile.name
        res.filetype = 'CSV'
        res.encoding = encoding
        reader = codecs.getreader(encoding)(infile)
        for line in reader:
            fields = line.rstrip().split('\t')
            if len(fields) == 2:
                key = fields[0].lower()
                if key == 'title':
                    res.title = fields[1]
                elif key == 'date':
                    res.date = datetime.datetime.strptime(fields[1], '%Y-%m-%d')
                elif key == 'copyright':
                    res.copyright = fields[1]
                elif key == 'dscale':
                    res.dmin, res.dmax = fields[1].split(',')
                    res.dmin = float(res.dmin)
                    res.dmax = float(res.dmax)
                elif key == 'hscale':
                    res.hmin, res.hmax = fields[1].split(',')
                    res.hmin = float(res.hmin)
                    res.hmax = float(res.hmax)
                elif key == 'sscale':
                    res.smin, res.smax = fields[1].split(',')
                    res.smin = float(res.smin)
                    res.smax = float(res.smax)
            elif len(fields) > 2 and fields[0][0] in '0123456789.+-':
                fields[0] = datetime.datetime.strptime (fields[0], "%H:%M:%S")
                for i in range (1, 10):
                    fields[i] = float(fields[i])
                res.append (
                    **dict(
                        zip(
                            ['time', 'distance', 'height', 'heart_rate',
                             'temperature', 'smooth_distance', 'smooth_height',
                             'speed', 'vspeed', 'slope', 'comment'],
                            fields)))
        res.is_smoothed = True
        res.speed_is_original = False
        res.recalc()
        return res

    @staticmethod
    def readGPX (infile):
        if _no_gpxdata:
            raise Exception("readGPX() requires module gpxdata")
        if isinstance (infile, basestring):
            # infile is a file name
            fp = open (infile, "rb")
            try:
                res = TourFile.readGPX (fp)
            finally:
                fp.close()
            return res
        # infile is a file object
        gpx = gpxdata.Document.readGPX (infile)
        # get first track
        track = gpx.tracks[0]
        # convert to Profile object
        res = TourFile (track.name, track.segments[0].points[0].t)
        res.filename = infile.name
        res.filetype = 'GPX'
        res.encoding = 'utf-8'
        s = 0.0
        for trkseg in track.segments:
            for i in range(len(trkseg.points)):
                p = trkseg.points[i]
                if i > 0:
                    s += trkseg.points[i-1].distance(p)
                res.append (
                    time=p.t, 
                    lat=p.lat,
                    lon=p.lon,
                    distance=round (s/1000.0, 3),
                    height=p.ele)
        res.is_smoothed = False
        res.speed_is_original = False
        res.recalc()
        return res

    @staticmethod
    def read (filename, encoding, filetype=None):
        if filetype == None:
            # guess filetype from filename
            fn = filename.lower()
            if fn.endswith ('.crp'):
                filetype = 'CRP'
            elif fn.endswith ('.csv'):
                filetype = 'CSV'
            elif fn.endswith ('.gpx'):
                filetype = 'GPX'
            else:
                raise Exception ("Can't determine file type")
        if filetype == 'CRP':
            return TourFile.readCRP (filename, encoding)
        elif filetype == 'CSV':
            return TourFile.readCSV (filename, encoding)
        elif filetype == 'GPX':
            return TourFile.readGPX (filename)
        else:
            raise Exception ('Unknown file type '+filetype)

    def writeCRP (self, outfile, encoding='iso-8859-1'):
        if isinstance (outfile, basestring):
            # outfile is a file name
            fp = open (outfile, "wb")
            try:
                self.writeCRP (fp)
            finally:
                fp.close()
            return
        # outfile is a file object
        self.filename = outfile.name
        self.filetype = 'CRP'
        self.encoding = encoding
        w = codecs.getwriter(encoding)(outfile)
        for i in range(len(self.points)):
            heart_rate = self.get (i, 'heart_rate')
            speed = self.get (i, 'speed')
            distance = self.get (i, 'distance')
            height = self.get (i, 'height')
            time = self.get (i, 'time')
            temperature = self.get (i, 'temperature')
            temperature = '%.1f' % (temperature if temperature != None else 0)
            temperature = temperature.replace ('.', ',')
            comment = self.get (i, 'comment')
            w.write (
                "%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\r\n" % (
                    round(heart_rate) if heart_rate != None else 0,
                    round(10*speed) if speed != None else 0,
                    round(100*distance) if distance != None else 0,
                    round(height) if height != None else 0,
                    0,
                    0,
                    temperature,
                    time.strftime ('%H:%M:%S') if time != None else '00:00:00',
                    comment if comment != None else ''
                    ))

    def writeCSV (self, outfile, encoding="utf-8"):
        if isinstance (outfile, basestring):
            # outfile is a file name
            fp = open (outfile, "wb")
            try:
                self.writeCSV (fp, encoding)
            finally:
                fp.close()
            return
        # outfile is a file object
        self.filename = outfile.name
        self.filetype = 'CSV'
        self.encoding = encoding
        w = codecs.getwriter(encoding)(outfile)
        w.write ("Encoding\t%s\n" % encoding)
        if self.title:
            w.write ("Title\t%s\n" % self.title)
        if self.date != None:
            w.write ("Date\t%s\n" % self.date.strftime("%Y-%m-%d"))
        if self.copyright:
            w.write ("Copyright\t%s\n" % self.copyright)
        if self.dmin != None and self.dmax != None:
            w.write ("Dscale\t%g,%g\n" % (self.dmin, self.dmax))
        if self.hmin != None and self.hmax != None:
            w.write ("Hscale\t%g,%g\n" % (self.hmin, self.hmax))
        if self.smin != None and self.smax != None:
            w.write ("Sscale\t%g,%g\n" % (self.smin, self.smax))
        for i in range(len(self.points)):
            w.write (
                "%s\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%s\n" % (
                    self.get (i, 'time').strftime ("%H:%M:%S"),
                    self.get (i, 'distance'),
                    self.get (i, 'height'),
                    self.get (i, 'heart_rate') or 0,
                    self.get (i, 'temperature') or 0,
                    self.get (i, 'smooth_distance') or 0,
                    self.get (i, 'smooth_height') or 0,
                    self.get (i, 'speed') or 0,
                    self.get (i, 'vspeed') or 0,
                    self.get (i, 'slope') or 0,
                    self.get (i, 'comment') or ""))

    def write (self, filename, encoding, filetype=None):
        if filetype == None:
            # guess filetype from filename
            fn = filename.lower()
            if fn.endswith ('.crp'):
                filetype = 'CRP'
            elif fn.endswith ('.csv'):
                filetype = 'CSV'
            else:
                raise Exception ("Can't determine file type")
        if filetype == 'CRP':
            self.writeCRP (filename, encoding)
        elif filetype == 'CSV':
            self.writeCSV (filename, encoding)
        else:
            raise Exception ('Unknown file type '+filetype)

# ----------------------------------------
