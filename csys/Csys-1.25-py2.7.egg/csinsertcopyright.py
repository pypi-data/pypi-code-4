#!/usr/local//bin/python

# $Header: /vol/cscvs/python-Csys/csinsertcopyright.py,v 1.1 2007/10/06 00:12:50 csoftmgr Exp $
# $Date: 2007/10/06 00:12:50 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: csinsertcopyright.py,v 1.1 2007/10/06 00:12:50 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

#	parser.add_option('-d', '--directory',
#		action='store', type='string', dest='directory', default=None,
#		help='Change to directory before starting process',
#	)
#	parser.add_option('-r', '--restart',
#		action='store_true', dest='restart', default=False,
#		help='restart without raising mailbox flags intially',
#	)
	return parser
#} setOptions

parser = setOptions()

(options, args) = parser.parse_args()

verbose = ''
if options.verbose: #{
	verbose = '-v'
	sys.stdout = sys.stderr
#}

Csys.getoptionsEnvironment(options)

copyrightfmt = ('''
%s

Copyright (c) 2000-2007 Celestial Software, LLC
Copyright (c) 2000-2007 Bill Campbell <bill@celestial.com>

This software may be copied under the terms of the GPL2 (Gnu
General Public Licence Version 2).

THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHORS AND COPYRIGHT HOLDERS AND THEIR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.
''')

copyright = copyrightfmt % Csys.Config.progname

startLinePattern = re.compile(r'^', re.DOTALL|re.MULTILINE)

def genCopyright(fname): #{
	base, ext = os.path.splitext(fname)
	sys.stderr.write('base >%s< ext >%s<\n' % (base, ext))
	copyright = copyrightfmt % fname
	if ext == '.py': #{{
		copyright = "\n__copyright__ = ('''\n%s\n''')" % copyright
	#}
	elif ext in ('.c', '.cc'): #{
		copyright = '\n#if 0\n%s\n#endif\n' % copyright
	#}
	else: #{
		copyright = startLinePattern.sub('## ', copyright)
	#}}
	return copyright
#} genCopyright

from fileinput import FileInput

fileinput = FileInput(
	files	= args, 
	inplace = True,
	backup	= '.bak',
)

needBlank = True
for line in fileinput: #{
	line = line[:-1]
	if fileinput.isfirstline(): #{
		needBlank = True
		fname = os.path.basename(fileinput.filename())
		sys.stderr.write('fname: %s\n' % fname)
	#}
	if needBlank and not line: #{
		needBlank = False
		print genCopyright(fname)
	#}
	print line
#}
