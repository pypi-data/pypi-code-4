import math
import string
import ast
###Constants

specialFuncts = ["log", "exp", "cos", "sin", "tan", "log10", "abs", "pi", "e"]

###
def pi():
    '''
    Returns pi constant
    '''
    return math.pi

###
def e():
    '''
    Returns e constant
    '''
    return math.e

###
def cos(x):
    '''
    Function to determinate the
    cosine value of x

    x: number
    
    Returns number
    '''
    return math.cos(x)

###
def sin(x):
    '''
    Function to determinate the
    sin value of x

    x: number
    
    Returns number
    '''
    return math.sin(x)

###
def abs(x):
    '''
    Function to determinate the
    absolute value of x

    x: number
    
    Returns number
    '''
    return math.fabs(x)

###
def log10(x):
    '''
    Function to determinate the decimal
    logarithm of x

    x: number
    
    Returns number
    '''
    return math.log10(x)

###
def log(x):
    '''
    Function to determinate the natural
    logarithm of x

    x: number
    
    Returns number
    '''
    return math.log(x)

###
def exp(x):
    '''
    Function to determinate the exponential
    of x

    x: number
    
    Returns number
    '''
    return math.exp(x)

###
def tan(x):
    '''
    Function to determinate the tangent
    of x

    x: number
    
    Returns number
    '''
    return math.tan(x)

###
def gotStr(mystr):

    s1 = string.ascii_lowercase
    s2 = string.ascii_uppercase
    s=s1+s2
    Result = False
    for i in mystr:
        if i in s:
            Result = True

    return Result

###
def isExpr(char):
    '''
    Function to determinate if a character is
    a valid character for a math expresion

    char: char
    
    Returns True or False
    '''
    s1 = string.ascii_lowercase
    s2 = string.ascii_uppercase
    numbers = [str(i) for i in range(0,100)]
    Result = True
    Result = Result and ((char in s1) or (char in s2) or (char in numbers))
    return Result

###
def remove_duplicates(l):
    '''
    Function to remove duplicates items from a
    list
    l: a list of string
    Returns a list
    '''
    return list(set(l))

###
def getVars(strExpr):
    '''
    Function to create a list of string of
    a math expressions, every item of the list
    is a valid math variable
    strExpr: String
    Returns list
    '''
    result=[]
    i=0
    mylen = len(strExpr)-1
    while i<=mylen:
        if isExpr(strExpr[i]):
            c=i
            s=''
            varFound=True
            while c<=(mylen) and varFound==True:
                if isExpr(strExpr[c]):
                    s+=strExpr[c]
                    c+=1
                else:
                    varFound=False
                
            if gotStr(s):
                result.append(s)
            i=c
        i+=1

    result2=[]
    numbers = [str(i) for i in range(0,10)]
    
    for i in result:
        if not(i in numbers):
            result2.append(i)

    result3 = remove_duplicates(result2)

    for i in specialFuncts:
        if i in result3:
            result3.remove(i)

    return result3

###
def recEvaluate(function, parameters, varList=[], bRepeated=False):

    myvars = []
    
    if (type(function)!=float and type(function)!=int):
        myvars = getVars(function)
        

    if len(myvars)>0:
        newParameters = addFunctions()
        
        for i in myvars:
            newParameters[i] = recEvaluate(parameters[i], parameters, varList, bRepeated)    
        return eval(function, newParameters)


    else:
        return eval(str(function), parameters)
        
###
def addFunctions():
    mydict = {}
    mydict['log']=log
    mydict['exp']=exp
    mydict['pi']=pi
    mydict['e']=e
    mydict['log10']=log10
    mydict['e']=e
    mydict['sin']=sin
    mydict['cos']=cos
    mydict['tan']=tan
    mydict['abs']=abs

    return mydict

###
class bigFunction(object):

    def __init__(self):

        self.data = {}
        self.function = ""
        self.pValues = {}

    def setFunction(self, function):
        """Set the global function to evaluate
    
        Keyword arguments:
        function (str) -- Variable designed in the global function
        """
        bSet = True
        
        import ast
        try:
           ast.parse(function)
           
        except SyntaxError as e:
            bSet = False
            print "A syntax error was found in function: "+function

        if bSet:
            self.function = function

    def addSub(self, var, function):
        """Add sub-functions to the collection

        Keyword arguments:
        var (str) -- Variable designed in the global function
        function (str) -- Sub-function
        """
        bSet = True
        
        import ast
        try:
           ast.parse(function)
           
        except SyntaxError as e:
            bSet = False
            print "A syntax error was found in function: "+function

        try:
           ast.parse(var)
           
        except SyntaxError as e:
            bSet = False
            print "A syntax error was found in variable: "+var

        if bSet:
            self.data[var] = function

    def updateSub(self, var, function):
        """Update sub-functions to the collection

        Keyword arguments:
        var (str) -- Variable to update
        function (str) -- Sub-function to update
        """
        bSet = True
        
        import ast
        try:
           ast.parse(function)
           
        except SyntaxError as e:
            bSet = False
            print "A syntax error was found in function: "+function

        try:
           ast.parse(var)
           
        except SyntaxError as e:
            bSet = False
            print "A syntax error was found in variable: "+var

        if bSet:
            if var in self.data.keys():
                self.data[var] = function
            else:
                print "variable "+var+" was not found"

    def evaluate(self, values = {}):

        """Evaluates global function within values

        Keyword arguments:
        values (dict) -- Variables and Values por parsing (default {})
        """

        result = None
        
        if self.function != "":
            if len(values)>0:
                for key, value in values.items():
                    self.data[key] = value
                
            try:
                result = recEvaluate(self.function, self.data)

            except KeyError as e:

                print "the key "+str(e)+" was not found in collection"

        return result
