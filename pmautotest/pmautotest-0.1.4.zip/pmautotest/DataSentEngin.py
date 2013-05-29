from Match import rangeCaseSelector,digitStandardizing
import log
sentLog = log.Logger("sentLog","info")

def caseSelector(range,model):
	match = rangeCaseSelector(range)
	matchCase = match[1]
	if match[0] == 9:
		sentLog.warning("Match Value Error")	
	elif match[0] == 1:
		bList = sentCase_A_or_B_to_C (matchCase)		
	elif match[0] == 2 : 
		bList = sentCase_A_or_B (matchCase)
	elif match[0] == 3 :
		bList = sentCase_A (range)
	elif match[0] == 4:
		bList = sentCase_M5_M6_M8 (matchCase,model)
	elif match[0] == 5:
		bList = sentCase_M6_M8_only (matchCase,model)
	elif match[0] == 6:
		bList = sentCase_double(matchCase)
	else:
		sentLog.warning( "No matched range:%s"%match[0])
	return bList
					
def sentCase_A_or_B_to_C (matchCase):# a or b to c
	sentLog.log_("Case 1 -> a or b to c")
	match = matchCase			
	valueA = digitStandardizing(match.group(1))			
	valueB = digitStandardizing(match.group(3))				
	valueC = digitStandardizing(match.group(5))	
	boundaryValue = [valueA,valueB,valueC]
	return boundaryValue

def sentCase_A_or_B (matchCase): # a to b
	sentLog.log_("Case 2 -> a or/to b")
	match = matchCase					
	valueA = digitStandardizing(match.group(1))			
	valueB = digitStandardizing(match.group(3))						
	boundaryValue = [ valueA, valueB]
	return boundaryValue
	
def sentCase_A(value_a):
	sentLog.log_("Compare a")
	valueA = digitStandardizing(value_a)
	boundaryValue = [ valueA ]
	return boundaryValue
	
def sentCase_M5_M6_M8(matchCase,model):
	sentLog.log_("Case 4:M5,M6,M8 selection")
	match = matchCase
	if model == "Model 05":
		newRange = ' '.join(match.group(1,2,3))
		boundaryValue = caseSelector(newRange,model)
	elif model == "Model 06" or model == "Model 08":
		newRange = ' '.join(match.group(6,7,8))
		boundaryValue = caseSelector(newRange,model)
	else:		
		sentLog.warning("Exception (check case 4):Not among M5,M6,or M8")
		return False
	return boundaryValue

def sentCase_M6_M8_only(matchCase,model):
	sentLog.log_("Case 5:M6,M8 only")
	match = matchCase
	if model == "Model 05":
		sentLog.debug("M5 doesn't have this param")
		return False
	elif model == "Model 06" or model == "Model 08":
		newRange = ' '.join(match.group(1,2,3))
		boundaryValue = caseSelector(newRange,model)
		sentLog.debug("%s New range:%s"%(model,newRange))
	else:		
		sentLog.warning("Exception (check case 5):Not among M5,M6,or M8")
		return False
	return boundaryValue

def sentCase_double(matchCase):
	match = matchCase
	sentLog.log_("Case 2 -> a or/to b  a or/to b")			
	valueA = digitStandardizing(match.group(1))			
	valueB = digitStandardizing(match.group(3))
	valueC = digitStandardizing(match.group(4))			
	valueD = digitStandardizing(match.group(6))
	boundaryValue = [valueA,valueB,valueC,valueD]
	return boundaryValue
