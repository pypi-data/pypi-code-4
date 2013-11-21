import urllib2, StringIO, gzip, os, xmlrpclib, struct, subdownloader.subDownLib.subtitlErrorHandler
from subdownloader.subDownLib.matrix import videoSupportedFormat, iso639LangCode

class openSubtitles(object):
	userAgent = "OS Test User Agent"
	username, password, res, token = "", "", "", ""
	language = "eng"
	server = None
	loggedin = 0
	selection = { 'enabled':False }

	def checkFormat(self,video):
		fileName, fileExtension = os.path.splitext(video)

		for extension in videoSupportedFormat:
			if '.' + extension == fileExtension:
				return True

		return False

	def LogIn(self):
		self.server = xmlrpclib.ServerProxy('http://api.opensubtitles.org/xml-rpc')
		self.res = self.server.LogIn(self.username, self.password, self.language, self.userAgent)

		if 'token' in self.res:
			self.token = self.res['token']
			return 1

		return 0

	def LogOut(self):
		self.res = self.server.LogOut ( self.token )
		if self.res['status'] == '200 OK':
			self.token = ""
			self.selection = { 'enabled':False }
			return 1
		else:
			return 0	

	# 0 : No subtitles found
	# 1 : Subtitle selected
	# 2 : I/O Error
	# 3 : Login First
	# 5 : Format not supported
	# 6 : Protocol Error
	# 7 : Connection timed out
	def searchSubtitle(self,Location,language):
		if not self.checkFormat(Location):
			return 5

		video_hash = self.hashFile(Location)

		if video_hash['status'] == 0:
			return 2;
		if self.token == "":
			return 3

		try:
			self.res = self.server.SearchSubtitles(self.token,[ {"sublanguageid":language, "moviehash":video_hash['hash'], "moviebytesize":video_hash['size']} ])
		except xmlrpclib.ProtocolError as err:
			return 6
		except socket.error as err:
			return 7

		if self.res['data'] == False:
			return 0

		self.selection = { 
			'enabled':True, 
			'SubDownloadLink':self.res['data'][0]['SubDownloadLink'],
			'SubFormat':self.res['data'][0]['SubFormat'],
			'SubLanguageID':self.res['data'][0]['SubLanguageID'],
			'OriginalVideoFile':Location
		}

		return 1

	# 2      : I/O Error
	# String : File name
	def downloadSubtitle(self,SubDownloadLink,SubFormat,SubLanguageID,video):
		try:
			video_path = os.path.dirname(os.path.realpath(video))
			video_basename = os.path.splitext(os.path.basename(video))[0]

			httpres = urllib2.urlopen(SubDownloadLink)
			compressedFile = StringIO.StringIO(httpres.read())
			decompressedFile = gzip.GzipFile(fileobj=compressedFile)
			outFilePath = video_path + '/' + video_basename + '.' + SubLanguageID + '.' + SubFormat

			with open(outFilePath, 'w') as outfile:
				outfile.write(decompressedFile.read())

			return outFilePath
		except(IOError):
			return 2

	# 4 : Not enabled
	def fetchSelection(self):
		if not self.selection['enabled']:
			return 4

		return self.downloadSubtitle(self.selection['SubDownloadLink'], self.selection['SubFormat'], self.selection['SubLanguageID'], self.selection['OriginalVideoFile'])

	def hashFile(self,name): 
		try: 
			longlongformat = 'q'  # long long 
			bytesize = struct.calcsize(longlongformat) 
			  
			f = open(name, "rb") 
			  
			filesize = os.path.getsize(name) 
			hash = filesize 
			  
			if filesize < 65536 * 2: 
				return {'statis':0, 'error':"SizeError"}
		 
			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
				 

			f.seek(max(0,filesize-65536),0) 
			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF 
		 
			f.close() 
			returnedhash =  "%016x" % hash 
			return {'status':1, 'hash':returnedhash, 'size':filesize}

		except(IOError): 
			return {'statis':0, 'error':"IOError"}
