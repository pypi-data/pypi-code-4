import re
import log
matchLog = log.Logger("matchLog","info")
def rangeCaseSelector(range,inst="999"):
    number_expr = '\D*\d+[,.Ee]*[-]*\d*[,.Ee]*[-]*\d*[,.Ee]*[-]*\d*' # Represent digits
    number_expr_without_minus = '\D*\d+[,.Ee]*\d*[,.Ee]*\d*[,.Ee]*\d*'
    word_expr = '\w+' # Represent 'or' ,'to'    
    matchLog.debug("Range: %s\n"%range)
    if re.match(r'(%s) (%s) (%s) (%s) (%s)\s*$'%(number_expr,word_expr,number_expr,
                            word_expr,number_expr),range):  #   (+/-)a or (+/-)b to c
        match = re.match(r'(%s) (%s) (%s) (%s) (%s)'%(number_expr,word_expr,number_expr,
                            word_expr,number_expr),range)
        matchLog.debug(" Match type:(+/-)a or (+/-)b to c\n\n ")    
        result = (1,match)
    elif re.match(r'(%s) (%s) (%s)\s*$'%(number_expr,word_expr,number_expr),range): # (+/-) a to/or (+/-) b
        match = re.match(r'(%s) (%s) (%s)'%(number_expr,word_expr,number_expr),range)
        matchLog.debug(" Match: (+/-) a to/or (+/-) b\n\n") 
        result = (2,match)
    elif re.match(r'%s$'%number_expr_without_minus,range):
        matchLog.debug(" Match A\n\n ")
        result = (3,"Certain number")
    else:
        if re.match(r'(%s) (%s) (%s) *(\(M.*) *(\n) *(%s) (%s) (%s)'%(number_expr,
                            word_expr,number_expr,number_expr,word_expr,number_expr),range):                
            match = re.match(r'(%s) (%s) (%s) *(\(M.*) *(\n) *(%s) (%s) (%s)'%(number_expr,
                            word_expr,number_expr,number_expr,word_expr,number_expr),range)
            matchLog.debug(" Match : Certain model ( M5, M6 or M8)\n\n")
            result = (4,match)
        elif re.match(r'(%s) (%s) (%s) *(\(M.*)'%(number_expr,word_expr,number_expr),range):
            match = re.match(r'(%s) (%s) (%s) *(\(M.*)'%(number_expr,word_expr,number_expr),range)
            matchLog.debug(" Match:Certain model ( M6,M8 only)\n\n ")           
            result = (5,match)
        elif re.match(r'(%s) (%s) (%s)\s+ (%s) (%s) (%s)\s*$'%(number_expr,word_expr,
                            number_expr,number_expr,word_expr,number_expr),range):
            match = re.match(r'(%s) (%s) (%s)\s+ (%s) (%s) (%s)\s*$'%(number_expr,
                            word_expr,number_expr,number_expr,word_expr,number_expr),range)
            matchLog.debug("Match: a to b  c to d\n\n" )
            result = (6,match)
        else:               
            matchLog.warning(" -----Warning: instance:%s --------\n"%inst)  
            matchLog.warning("Range: %s\n"%range)
            matchLog.warning("Not Match any range type\n\n")
            result = (9,"This type")
        
    #print debug_stream
    #print match.groups()
    
    return result

def digitStandardizing(digit):
    pA = re.compile(r'\,')
    pB = re.compile(r'\+\/\-')  
    digit = pA.sub('',digit)            
    std_digit = pB.sub('',digit)
    return std_digit