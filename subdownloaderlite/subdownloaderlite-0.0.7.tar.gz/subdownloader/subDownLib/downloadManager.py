import opensubtitles, os
from subdownloader.subDownLib.matrix import videoSupportedFormat, iso639LangCode

class downloadManager(opensubtitles.openSubtitles):
#	def connect(self):
#	def disconnect(self):
	lastLangCheckStatus = { 'code':'eng', 'status':True }

	def checkIfSubtitleIsNeeded(self,video,lang):
		video_path = os.path.dirname(os.path.realpath(video))
		video_basename = os.path.splitext(os.path.basename(video))[0]
		video_subtitle_file = video_path + '/' + video_basename + '.' + lang + '.srt'

		return not os.path.isfile(video_subtitle_file)

	def DownloadSingle(self,Video,Language):
		if not self.checkLanguage(Language):
			print "Language " + Language + " not supported"
			return 0

	        print "Serching subtitle for file : " + Video

		retVal = self.searchSubtitle(Video,Language)
		if retVal == 0:
			print "\tNo subtitle found"
			return 0
		if retVal == 7:
			print "\tConnection timed out"
			return 0
		if retVal == 6:
			print "\tService Unaviable"
			return 0
		if retVal != 1:
                	print "\tError code detected"
                	return 0

        	print "\tFetching subtitle...\n\tResult - " + self.fetchSelection()

        	return 1

	def DownloadFolder(self,Folder,Language):
		if not self.checkLanguage(Language):
			print "Language " + Language + " not supported"
			return 0
		for root, dirs, files in os.walk(Folder):
			for file in files:
				for ext in videoSupportedFormat:
					filename = os.path.join(root, file)
					if file.endswith(ext):
						if self.checkIfSubtitleIsNeeded(filename,Language):
							self.DownloadSingle(filename,Language)
						else:
							print filename + " already have " + Language + " subtitle"

	def checkLanguage(self,Language):
		if self.lastLangCheckStatus['code'] == Language:
			return self.lastLangCheckStatus['status']

		for lang in iso639LangCode:
			if lang == Language:
				self.lastLangCheckStatus = { 'code':Language, 'status':True }
				return True

		lastLangCheckStatus = { 'code':Language, 'status':False }
		return False
