import re
import log
from Match import rangeCaseSelector,digitStandardizing

checkLog = log.Logger("checkLog","warning")
def compare_a_to_b(boundary_a,boundary_b,num_for_check):
	checkLog.debug("Compare a to b")
	try:
		in_range = float(num_for_check) >= float(boundary_a) and float(num_for_check) <= float(boundary_b)
	except: #"ValueError":
		checkLog.warning("Exception while comparing 'a to b'")
		return False
	if in_range:
		checkLog.debug("True.\n%s is between %s and %s"%(num_for_check,boundary_a,boundary_b))
	else:
		checkLog.debug("False.\n%s is NOT between %s and %s"%(num_for_check,boundary_a,boundary_b))
	return in_range

def compare_a_or_b(value_a,value_b,num_for_check):
	checkLog.debug("Compare a or b")
	try:
		in_range = float(num_for_check) == float(value_a) or float(num_for_check) == float(value_b)					
	except: 					
		checkLog.warning("Exception while comparing 'a or b")
		return False
	if in_range:
		checkLog.debug("True.\n%s is in range %s or %s"%(num_for_check,value_a,value_b))
	else:
		checkLog.debug("False.\n%s is Out of range %s and %s"%(num_for_check,value_a,value_b))
	return in_range
	
def compare_a(value_a,num_for_check):
	checkLog.log_("Compare a")
	try:
		value_A = digitStandardizing(value_a)
		in_range = float(num_for_check) == float(value_A)				
	except: 
		checkLog.warning("Exception")
		return False
	if in_range:
		checkLog.debug("True.\n%s is equal to %s"%(num_for_check,value_a))
	return in_range

def check_case_1 (num_for_check,match_case):# a or b to c
	checkLog.log_("Case 1 -> a or b to c")
	match = match_case			
	value_A = digitStandardizing(match.group(1))			
	value_B = digitStandardizing(match.group(3))				
	value_C = digitStandardizing(match.group(5))	
	
	if float(num_for_check) == float(value_A):
		checkLog.debug("ok,%s = value_A\n"%num_for_check)	
		is_valid = True
	else:	
		is_valid = compare_a_to_b(value_B,value_C,num_for_check)
	return is_valid

def check_case_2 (num_for_check,match_case): # a to b
	checkLog.log_("Case 2 -> a or/to b")
	match = match_case					
	value_A = digitStandardizing(match.group(1))			
	value_B = digitStandardizing(match.group(3))						
	if match.group(2) == 'to':	
		match = match.group()
		if re.match(r'(\+\/\-)',match) and float(value_A) == 0:
			is_valid = compare_a_to_b("-%s"%value_B,value_B,num_for_check)
		else:
			is_valid = compare_a_to_b(value_A,value_B,num_for_check)
	elif match.group(2) == 'or':
		is_valid = compare_a_or_b(value_A,value_B,num_for_check)
	else:
		checkLog.warning("Exception (check case 2)")
		is_valid = False
	return is_valid

		
def check_case_3(value_a,num_for_check):
	checkLog.log_("Compare a")
	try:
		value_A = digitStandardizing(value_a)
		in_range = float(num_for_check) == float(value_A)				
	except: 
		checkLog.warning("Exception")
		return False
	if in_range:
		checkLog.debug("True.\n%s is equal to %s"%(num_for_check,value_a))
	return in_range
	
def check_case_4(num_for_check,match_case,model):
	checkLog.log_("Case 4:M5,M6,M8 selection")
	match = match_case
	if model == "Model 05":
		new_range = ' '.join(match.group(1,2,3))
		checkLog.debug("Model %s's range:%s"%(model,new_range))
		return check_validity(num_for_check,new_range,inst=999)
		#check_case_2(num_for_check,match_case)
	elif model == "Model 06" or model == "Model 08":
		new_range = ' '.join(match.group(6,7,8))
		checkLog.debug("Model %s's range:%s"%(model,new_range))
		return check_validity(num_for_check,new_range,inst=999)	
	else:		
		checkLog.warning("Exception (check case 4):Not among M5,M6,or M8")
		return False

def check_case_5(num_for_check,match_case,model):
	checkLog.log_("Case 5:M6,M8 only")
	match = match_case
	if model == "Model 05":
		checkLog.debug("M5 doesn't have this param")
		return True
	elif model == "Model 06" or model == "Model 08":
		new_range = ' '.join(match.group(1,2,3))
		checkLog.debug("%s New range:%s"%(model,new_range))
		print "Model %s's range:%s"%(model,new_range)
		return check_validity(num_for_check,new_range,inst=999)	
	else:		
		checkLog.warning("Exception (check case 5):Not among M5,M6,or M8")
		return False

def check_case_6(num_for_check,match_case,model):
	match = match_case
	checkLog.log_("Case 2 -> a or/to b  a or/to b")			
	value_A = digitStandardizing(match.group(1))			
	value_B = digitStandardizing(match.group(3))
	value_C = digitStandardizing(match.group(4))			
	value_D = digitStandardizing(match.group(6))
	if match.group(2) == 'to' and match.group(5) == 'to':	
		is_valid = compare_a_to_b(value_A,value_B,num_for_check) or compare_a_to_b(value_C,value_D,num_for_check)
	else:
		checkLog.warning("Exception (check case 6)")
		is_valid = False
	return is_valid
	
		
def check_validity(num_for_check,range,model = "Model 05",inst=100):
	'''Check value 
	'''
	range_type = rangeCaseSelector(range,inst)	
	match_case = range_type[1]
	checkLog.debug("\n********inst:%s************\
		\nNum_for_check:%s\nrange:%s"%(inst,num_for_check,range))
	if range_type[0] == 9:
		checkLog.warning("Match Value Error")
		is_valid = False
		#is_valid = True
		
	elif  range_type[0] == 1:
		is_valid = check_case_1(num_for_check,match_case)		
		if not is_valid:
			checkLog.warning("Case 1")
	elif range_type[0] == 2 : 
		is_valid = check_case_2 (num_for_check,match_case)
		if not is_valid:
			checkLog.warning("Case 2")
	elif range_type[0] == 3 :
		is_valid = check_case_3(range,num_for_check)
		if not is_valid:
			checkLog.warning("Case 3")	
	elif range_type[0] == 4:
		is_valid = check_case_4(num_for_check,match_case,model)
		if not is_valid:
			checkLog.warning("Case 4")
	elif range_type[0] == 5:
		is_valid = check_case_5(num_for_check,match_case,model)
		if not is_valid:
			checkLog.warning("Case 5")
	elif range_type[0] == 6:
		is_valid = check_case_6(num_for_check,match_case,model)
		if not is_valid:
			checkLog.warning("Case 6")
	else:
		checkLog.warning( "No matched range:%s"%range_type[0])
		is_valid = False
					
	if not is_valid:
		checkLog.warning("\nInst:%s\nNum_for_check:%s \nrange:%s\nOut of range\n"%(inst,num_for_check,range))
		#autoLog.log_("Value:%s "%num_for_check)
		#autoLog.log_("Range:%s\t->\tOut of range"%range)
	else:
		checkLog.debug("Inst:%s\nNum_for_check:%s is in range:%s\n"%(inst,num_for_check,range))
	return  is_valid
		
	
	

def get_boundary_value(range,border_class="min"):
	if re.match(r'(\D*\d+\D*\d*\D*\d*) (\w+) (\D*\d+\D*\d*\D*\d*) (\w+) (\D*\d+\D*\d*\D*\d*)',range):	#	(+/-)a or (+/-)b to c
			match = re.match(r'(\D*\d+\D*\d*\D*\d*) (\w+) (\D*\d+\D*\d*\D*\d*) (\w*) (\D*\d*\D*\d*\D*\d*)',range)
			
			pA = re.compile(r'\,')
			value_A = pA.sub('',match.group(1))
			
			pB = re.compile(r'\,')
			value_B = pB.sub('',match.group(3))
				
			pC = re.compile(r'\,')
			value_C = pC.sub('',match.group(5))	
			
			if border_class == "min":
				return float(value_B)
			elif border_class == "middle":
				return (float(value_B)+float(value_C))/2
			elif border_class == "max":
				return float(value_C)
			else:
				print "border class error1"
				
	elif re.match(r'(\D*\d+\D*\d*\D*\d*) (\w+) (\D*\d+\D*\d*\D*\d*)',range): # (+/-) a to/or (+/-) b
			match = re.match(r'(\D*\d+\D*\d*\D*\d*) (\w+) (\D*\d+\D*\d*\D*\d*)',range) 
			
			pA = re.compile(r'\,')
			value_A = pA.sub('',match.group(1))			
			pB = re.compile(r'\,')
			value_B = pB.sub('',match.group(3))
			
			if match.group(2) == 'to':	
				if border_class == "min":
					return float(value_A)
				elif border_class == "middle":
					return (float(value_A)+float(value_B))/2
				elif border_class == "max":
					return float(value_C)
				else:
					print "border class error2"
			elif match.group(2) == 'or':
				if border_class == "min":
					return float(value_A)
				elif border_class == "middle":
					return (float(value_A)+float(value_B))/2
				elif border_class == "max":
					return float(value_B)
				else:
					print "border class error2"
	elif re.match(r'\D*\d+\W*\d*$',range):
			return float(range)
	else:
			print "range:",range
			print "Not match"