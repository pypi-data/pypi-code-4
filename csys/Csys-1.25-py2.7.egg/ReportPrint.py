import Csys, sys

class ReportPrint(Csys.CSClass): #{
	_attributes = dict(
		company		= 'Celestial Software LLC',
		title		= '',
		title1		= '',
		progname	= Csys.Config.progname,
		version		= '0.00',
		header1		= '',
		width		= 132,
		lefttitle	= '',
		period		= '',
		subtitle	= '',
		lasttitle	= '',
		pagelgth	= 66,
		printlgth	= 60,
		filehandle	= sys.__stdout__,
		pageno		= 0,
		_curline	= 0,
		_uscore		= '',
	)
	def __init__(self, **kwargs): #{
		Csys.CSClass.__init__(self, True, **kwargs)
		self._uscore = ' ' + '-' * self.width
		self._progver = '[%s,v %s]' % (self.progname, self.version)
		# self._curline = self.pagelgth
	#} __init__

	def fmtline(self, left, middle, right=''): #{
		'''Formats line with left, centered, and right justified titles.'''
		# length of left field to position center field
		centerPosition	= (self.width - len(middle)) / 2
		rightPosition	= self.width - len(right)
		middleLength	= rightPosition - centerPosition
		fmt = '%%-%ds%%-%ds%%s' % (centerPosition, middleLength)
		return fmt % (left, middle, right)
	#}

	def write(self, msg, need=1, numberlines=False): #{
		'''Check for page overflow then write line'''
		if self._curline + need > self.printlgth: self.writeHeader()
		msg = str(msg).rstrip()
		lines = msg.split('\n')
		if len(lines) > 1: #{
			for line in lines: self.write(line, numberlines=numberlines)
		#}
		else: #{
			self._curline += 1
			msg = str(msg).rstrip()[:self.width]
			if numberlines: self.filehandle.write('%3d %s\n' % (self._curline, msg))
			else: self.filehandle.write('%s\n' % msg)
		#}}
		# self.filehandle.write('')
	#} write

	def skip(self): #{
		'''Skip to next page and print header'''
		if self._curline: #{
			linesrem = self.pagelgth - self._curline
			if linesrem > 0: self.filehandle.write('\n' * linesrem)
			self._curline = 0
		#}
	#} skip
	def writeHeader(self): #{
		'''Print header'''
		self.skip()
		import time
		t = time.localtime(time.time())
		left = 'Date: ' + time.strftime('%m/%d/%Y', t)
		self.pageno += 1
		right = 'Page: %d' % self.pageno
		self.write(self.fmtline(left, self.company, right))
		left = 'Time: ' + time.strftime('%H:%M:%S', t)
		self.write(self.fmtline(left, self.title, self._progver))
		if self.title1 or self.lefttitle: #{
			self.write(self.fmtline(self.lefttitle, self.title1, ''))
			self.write('\n')
		#}
		if self.subtitle: #{
			self.write(self.fmtline('', self.subtitle, ''))
			self.write('\n')
		#}
		if self.lasttitle: #{
			self.write('')
			self.write(self.lasttitle)
		#}
		self.write(self._uscore)
	#}
#} class ReportPrint

from cStringIO import StringIO

_filehandle = StringIO()

_docPrint = ReportPrint(
	filehandle	= _filehandle,
	company		= 'Company Header',
	title		= 'title',
	title1		= 'title1',
	lefttitle	= 'lefttitle',
	header1		= 'header1',
	progname	= 'progname',
	version		= 'version',
	width		= 74,
	period		= 'Period: xxx through yyy',
	subtitle	= 'subtitle',
	lasttitle	= 'lasttitle (left justified)'
)

_docPrint.writeHeader()

_doctxt = ('''
ReportPrint is a module to automatically generate printed
headers with sufficient information.

Usage:
    The ReportPrint class may be called with a variety of
    keyword arguments.  The example below shows all options and
    their default values.  Empty titles and subtitles will not
    result in blank lines.

    from Csys.ReportPrint import ReportPrint

    printer = ReportPrint(
        company     = 'Celestial Software LLC',
        title       = '',
        title1      = '',
        progname    = Csys.Config.progname,
        version     = '0.00',
        header1     = '',
        width       = 132,
        lefttitle   = '',
        period      = '',
        subtitle    = '',
        lasttitle   = '',
        pagelgth    = 66,
        printlgth   = 60,
        filehandle  = sys.__stdout__,
        pageno      = 0,
    )

    printer.writeHeader()
    for someloop:
        # ...
        printer.write(msg, [need=lines], [numberlines=True])

Methods:
    write(msg, need=1, numberlines=False)

        This writes the string msg, splitting on newlines to
        properly keep track of line count.

        The ``need'' paramter is the number of lines needed on
        the page before printing the first line in msg.  This is
        useful when writing reports where one wants to avoid
        widow lines at the end of the page.

        The ``numberlines'' paramter prints line numbers on ever
        line of the page.  This may be useful for debugging or
        forms generation.
''')

_docPrint.write(_doctxt)
_filehandle.seek(0)

__doc__ = '\n'.join([line.rstrip() for line in _filehandle])

if __name__ == '__main__': #{
	t = ReportPrint()
	print 'OK'
	print __doc__
#}
