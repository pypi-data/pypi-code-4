#!/usr/bin/env python
""" A python library for reading PTW mcc files
      Graham Arden, January 2011 """


class mc2:
	
	"""Defines an mc2 class with the required attributes"""
	
	def __init__(self, measdate, linac, modality, inplane_axis, crossplane_axis, depth_axis, inplane_axis_dir, crossplane_axis_dir, depth_axis_dir, energy, ssd, field_inplane, field_crossplane, scan_curvetype, scan_depth, scan_offaxis_inplane, scan_offaxis_crossplane, meas_time, meas_unit, xdata, ydata, refdata):		
		self.measdate = measdate
		self.linac = linac
		self.modality = modality
		self.inplane_axis = inplane_axis
		self.crossplane_axis = crossplane_axis
		self.depth_axis = depth_axis
		self.inplane_axis_dir =  inplane_axis_dir
		self.crossplane_axis_dir = crossplane_axis_dir
		self.depth_axis_dir = depth_axis_dir
		self.energy = energy
		self.ssd = ssd
		self.field_inplane = field_inplane
		self.field_crossplane = field_crossplane
		self.scan_curvetype = scan_curvetype
		self.scan_depth = scan_depth
		self.scan_offaxis_inplane = scan_offaxis_inplane
		self.scan_offaxis_crossplane = scan_offaxis_crossplane
		self.meas_time = meas_time
		self.meas_unit = meas_unit	
		self.xdata = xdata
		self.ydata = ydata
		self.refdata = refdata

def read_mc2(file, datastartline, dataendline):
	
	"""Read data from the mc2 file and present it as an instance of the mc2 class	
	As files can contain more than one dataset the start and end line numbers
	need to be supplied.
	These can be obtained using datasetinfo(file)	
	Use as dataset = read_mc2(file, datastartline, dataendline)"""	
	
	import numpy
	
	lineNumber = 0
	dataline = 0
	ifile = open(file, 'r') 
	lines = ifile.readlines()
	linac="N/A"  # earlier vesions of the mc2 software didn't include this field, if its missing then N/A will be returned instead
	
	for line in lines:
		line = line.replace('\t', ',')  # replaces tabs with commas
		line = line.rstrip('\r\n')         # strips control characters from the end of the line
		
		if (lineNumber > datastartline) and (lineNumber < dataendline):
			if "MEAS_DATE" in line:
				measdate = (line.split("=")[1])
				
			if "LINAC" in line:
				linac = (line.split("=")[1])
						
			if "MODALITY=" in line:
				modality = (line.split("=")[1])
				
			if "INPLANE_AXIS=" in line:
				inplane_axis = (line.split("=")[1])
				
			if "CROSSPLANE_AXIS=" in line:
				crossplane_axis = (line.split("=")[1])

			if "DEPTH_AXIS=" in line:
				depth_axis = (line.split("=")[1])
			
			if "INPLANE_AXIS_DIR=" in line:
				inplane_axis_dir = (line.split("=")[1])
				
			if "CROSSPLANE_AXIS_DIR=" in line:
				crossplane_axis_dir = (line.split("=")[1])
				
			if "DEPTH_AXIS_DIR=" in line:
				depth_axis_dir = (line.split("=")[1])
				
			if "ENERGY" in line:
				energy = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
				
			if "SSD=" in line:
				ssd = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
				
			
			if ("FIELD_INPLANE" in line) and ("REF" not in line):
				field_inplane=(int((line.split("=")[1]).split('.')[0]))# converts from text to an integer
			
			if  ("FIELD_CROSSPLANE" in line) and ("REF" not in line):
				field_crossplane = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
				
			if "SCAN_CURVETYPE" in line:
				scan_curvetype = (line.split("=")[1])
				
			if "SCAN_DEPTH=" in line:
				scan_depth  = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
			
			if "SCAN_OFFAXIS_INPLANE=" in line:
				scan_offaxis_inplane = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
				
			if "SCAN_OFFAXIS_CROSSPLANE=" in line:
				scan_offaxis_crossplane = (int((line.split("=")[1]).split('.')[0])) # converts from text to an integer
				
			if "MEAS_TIME=" in line:
				meas_time = (line.split("=")[1])
				
			if "MEAS_UNIT=" in line:
				meas_unit = (line.split("=")[1])
				
			if line.startswith(',,,'):     # this must be our data
				if dataline == 0:
					xvalue, yvalue, refvalue = extractdata(line)
					xdata = numpy.zeros(0)
					xdata = xvalue
					ydata = numpy.zeros(0)
					ydata = yvalue
					refdata = numpy.zeros(0)
					refdata = refvalue
				else:
					xvalue, yvalue, refvalue = extractdata(line)
					xdata = numpy.hstack([xdata, xvalue])
					ydata = numpy.hstack([ydata, yvalue])
					refdata = numpy.hstack([refdata, refvalue])
				dataline = dataline + 1
				
			if "END_DATA" in line:   #we have now reached the end of aour data and can create our class
				mc2_dataset = mc2(measdate, linac, modality, inplane_axis, crossplane_axis, depth_axis, inplane_axis_dir, crossplane_axis_dir, depth_axis_dir, energy, ssd, field_inplane, field_crossplane, scan_curvetype, scan_depth, scan_offaxis_inplane, scan_offaxis_crossplane, meas_time, meas_unit, xdata, ydata, refdata)	
				
		lineNumber = lineNumber + 1
		
	return mc2_dataset	
	

def open_mcc(dataDirectory):
	
	"""A really simple function which presents a GUI to allow the user to select a file"""
	
	import Tkinter, tkFileDialog
	root = Tkinter.Tk()
	root.withdraw()
	mccFileName = tkFileDialog.askopenfilename(title = "select the mcc file", initialdir=dataDirectory)
	return mccFileName


def extractdata(line):
	
	"""For each line, return the x and y values, check whether there is reference value
	and if so return the reference value, otherwise return a reference	value of 1 """
	
	newArray = (line.split(','))  # 
	if len(newArray) == 8:
		# convert the strings to floats
		xvalue = float(newArray[3])
		yvalue =  float(newArray[5])
		refvalue =  float(newArray[7])
		return xvalue, yvalue, refvalue
	if len(newArray) == 6:
		# convert the strings to floats
		xvalue = float(newArray[3])
		yvalue =  float(newArray[5])
		refvalue = 1
		return xvalue, yvalue, refvalue
	else:
		print "Houston, we have a problem, This line does not appear to be data!:"
		print line


def datasetinfo(file):
	
	"""Finds datasets within a file and returns some useful info so you can decide
	which one you need
	Returns the start and end lines, acquisition date, energy,field size, direction and depth
	Call as 'DataStart, DataEnd, MeasDate, Energy, FieldSize, Depth=datasetinfo(inputfile)' """
	
	datasets = 0
	ifile = open(file, 'r') 
	lines = ifile.readlines()
	datasets = 0
	lineNumber = 0	
	BeginScan=[]; EndScan=[]; MeasDate = []; Energy = []; FieldSize=[]; Depth=[]; Direction=[]
	for line in lines:
		
		line = line.replace('\t', ',')      # replaces all the tabs with commas
		line = line.rstrip('\r\n')            # strips any control characters from the end of the line
		
		if ("BEGIN_SCAN" in line) and ("DATA" not in line):
			BeginScan.append(lineNumber)
			datasets = datasets+1
			
		if "MEAS_DATE" in line:
			MeasDate.append(line.split("=")[1])
			
		if "ENERGY" in line:
			Energy.append(int((line.split("=")[1]).split('.')[0]))
			# This rather convoluted line extracts the integer from a string 
			# e.g the string "6.00" is converted to the integer "6"
			#  Energy=(int(line.split('.')[0]))

		if "SCAN_DEPTH=" in line:
			Depth.append(int((line.split("=")[1]).split('.')[0]))
			
		if ("FIELD_INPLANE" in line) and ("REF" not in line):
			FieldSize.append((int((line.split("=")[1]).split('.')[0]))/10) # convert from mm to cm
		3		
		#
		# This probably shouldn't be relied upon as the direction
		# in the old data appears to be quite unreliable.
		# The filename appears to be a more reliable guide to the scan direction!
		#
		
		if "SCAN_CURVETYPE=" in line:			
			answer = (line.split("=")[1])
			if (line.split("=")[1]) == "CROSSPLANE_PROFILE":
				Direction.append("AB(X)")
			if (line.split("=")[1]) == "INPLANE_PROFILE":
				Direction.append("GT(Y)")

		if ("END_SCAN" in line) and ("DATA" not in line):
			EndScan.append(lineNumber)	
			
		lineNumber = lineNumber + 1		
	return BeginScan, EndScan, MeasDate, Energy, FieldSize, Depth, Direction




	

