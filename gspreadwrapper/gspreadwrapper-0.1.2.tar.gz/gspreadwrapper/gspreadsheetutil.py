import gspread
import getopt
import sys

class GspreadsheetUtil:
	def __init__(self, email, password, id, column_id):

		self.email = email
		self.password = password
		self.id = str(id)
		self.column_id = int(column_id)
		self.gc = self._getGspreadClient()

	def _getGspreadClient(self):
		try:
			return gspread.login(self.email, self.password)

		except gspread.exceptions.AuthenticationError as err:
			#needed as gspread lib doesnt properly handle errors yet
			raise WrapperError("Incorrect authentication")
	
	def returnSingleColumnFirstWorksheet(self):
		try:
			sh = self.gc.open_by_key(self.id)
			#always retrieves first worksheet
			wh = sh.get_worksheet(0)
			if wh is None:
				raise WrapperError("Worksheet Not Found")
			return wh.col_values(self.column_id)

		except gspread.exceptions.SpreadsheetNotFound as err:
		#needed as gspread lib doesnt properly handle errors yet
			raise WrapperError("Spreadsheet Not Found")


class WrapperError( Exception ): pass



	
def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw=","id=", "column="])
  except getopt.error, msg:
    print 'python gspreadsheetutil.py --user [username] --pw [password] --id [spreadsheet id] --column [column id] '
    sys.exit(2)
  
  user = ''
  pw = ''
  title = ''
  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a
    elif o == "--id":
      id= a
    elif o == "--column":
      column = a

  if user == '' or pw == '' or id == '' or column== '':
    print 'python gspreadsheetutil.py --user [username] --pw [password] --id [spreadsheet id] --column [column id] '
    sys.exit(2)
        

  try:
	gSpreadsheet = GspreadsheetUtil(user, pw, id, column)
	#get a set without column header
	column_set=set(gSpreadsheet.returnSingleColumnFirstWorksheet()[1:])
  except WrapperError as err:
  	print str(err)
  	exit()
  for cell in column_set:
  	print cell


if __name__ == '__main__':
  main()