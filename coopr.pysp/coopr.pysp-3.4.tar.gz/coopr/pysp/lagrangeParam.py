#! /usr/bin/env python

# This is virgin parametric lagrange multiplier search
# no pre-processing and no gap-closing...just testing algorithm

import sys
import os
import inspect  # used for debug when Result was not returning correctly
import random
import math 
import time 
import datetime
import operator
import types
from coopr.pysp.scenariotree import *
from coopr.pysp.phinit import *
from coopr.pysp.ph import *
from coopr.pysp.ef import *
from coopr.opt import SolverFactory

import coopr.pysp.lagrangeutils as lagrUtil
##############################################################

###################################
def run(args=None):
###################################

   print "RUNNING - run args=",args

   def LagrangeParametric(args=None):
      class Object(object): pass
      Result = Object()
      Result.status = 'LagrangeParam begins '+ str(datetime.datetime.now()) + '...running new ph'
      def new_ph():
         reference_model, scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory = load_models(options)
         if reference_model is None or scenario_tree is None:
            print "internal error in new_ph"
            exit(2)
         retval= create_ph_from_scratch(options, reference_model, scenario_tree, unarchived_model_directory, unarchived_instance_directory)
         return retval

      blanks = "                          "  # used for formatting print statements
# options used
      alphaMin      = options.alpha_min
      alphaMax      = options.alpha_max
      alphaTol      = options.alpha_tol
      Lgap          = options.Lagrange_gap
      minProb       = options.min_prob
      maxIntervals  = options.max_intervals
      maxTime       = options.max_time
      IndVarName    = options.indicator_var_name
      multName      = options.lambda_parm_name
      CCStageNum    = options.stage_num
      csvPrefix     = options.csvPrefix
      verbosity     = options.verbosity
#      verbosity = 2 # override for debug (= 3 to get super-debug)
      HGdebug = 0   # special debug (not public)
####################################################################
      STARTTIME = time.time()

      Result.status = "options set"
      if verbosity > 1: 
        print "From LagrangeParametric, status =",getattr(Result,'status'), \
            "\tSTARTTIME =",STARTTIME

      ph = new_ph() 
      Result.ph = ph
      rootnode = ph._scenario_tree._stages[0]._tree_nodes[0]   # use rootnode to loop over scenarios

      if find_active_objective(ph._scenario_tree._scenarios[0]._instance,safety_checks=True).is_minimizing():
         sense = 'min'
      else:
         sense = 'max'

      scenario_count = len(full_scenario_tree._stages[-1]._tree_nodes)
      if options.verbosity > 0: print sense,scenario_count,"scenarios\n"

# initialize
      Result.status = 'starting at '+str(datetime.datetime.now())
      if verbosity > 0: print Result.status
      ScenarioList = []
      lambdaval = 0.
      lagrUtil.Set_ParmValue(ph, multName,lambdaval)
      sumprob = 0.
      minprob = 1.
      maxprob = 0.
      for scenario in rootnode._scenarios:
         instance = ph._instances[scenario._name]
         sname = scenario._name
         sprob = scenario._probability
         sumprob = sumprob + sprob
         minprob = min(minprob,sprob)
         maxprob = max(maxprob,sprob)
         ScenarioList.append([sname,sprob])
         getattr(instance,IndVarName).value = 0   # fixed = 0 to get PR point at b=0
         getattr(instance,IndVarName).fixed = True
      instance.preprocess()
      ScenarioList.sort(key=operator.itemgetter(1))   # sorts from min to max probability
      if verbosity > 0: print "probabilities sum to",sumprob,"range: ",minprob,"to",maxprob
      Result.ScenarioList = ScenarioList

# Write ScenarioList = name, probability in csv file sorted by probability 
      outName = csvPrefix + 'ScenarioList.csv'
      print "writing to ",outName
      outFile = file(outName,'w')
      for scenario in ScenarioList: print >>outFile, scenario[0]+ ", " +str(scenario[1])
      outFile.close()
      Result.ScenarioList = ScenarioList

      addstatus = 'Scenario List written to ' + csvPrefix+'ScenarioList.csv'
      Result.status = Result.status + '\n' + addstatus
      if verbosity > 0: print addstatus
 
      if verbosity > 0: print "\nlambda=",lambdaval,"...solve begins",str(datetime.datetime.now())
      SolStat, zL = lagrUtil.solve_ph_code(ph, options)
      if verbosity > 0: print "\tsolve ends",str(datetime.datetime.now()),"with status =",SolStat

      bL = Compute_ExpectationforVariable(ph, IndVarName, CCStageNum)
      if bL > 0:
         print "** bL =",bL," > 0 (all ",IndVarName,"= 0)"
         return Result

      if verbosity > 0:  print "Initial optimal obj =",zL,"for bL =",bL

      for scenario in ScenarioList:
         sname = scenario[0]
         instance = ph._instances[sname]
         getattr(instance,IndVarName).value = 1  # fixed = 1 to get PR point at b=1
      instance.preprocess() 
      
      if verbosity > 0: 
        print "\nlambda=",lambdaval,"...solve begins",str(datetime.datetime.now())
      SolStat, zU = lagrUtil.solve_ph_code(ph, options)
      if verbosity > 0: 
        print "\tsolve ends",str(datetime.datetime.now()),"with status =",SolStat     
      if not SolStat[0:3] == 'opt':
         print SolStat[0:3]," is not ",'opt'
         addstatus = "** Solution is non-optimal...aborting"
         print addstatus
         Result.status = Result.status + "\n" + addstatus
         return Result

      bU = Compute_ExpectationforVariable(ph, IndVarName, CCStageNum)
      if bU < 1.- alphaTol and verbosity > 0: 
        print "** Warning:  bU =",bU," < 1"

      
### enumerate points in PR space (all but one scenario)
#      Result.lbz = [ [0,bL,zL], [None,bU,zU] ]
#      for scenario in rootnode._scenarios:
#         sname = scenario._name
#         instance = ph._instances[sname]
#         print "excluding scenario",sname
#         getattr(instance,IndVarName).value = 0
#         print sname,"value =",getattr(instance,IndVarName).value,getattr(instance,IndVarName).fixed
#         SolStat, z = lagrUtil.solve_ph_code(ph, options)
#         b = Compute_ExpectationforVariable(ph, IndVarName, CCStageNum)
#         print "solve ends with status =",SolStat,"(b, z) =",b,z
#         getattr(instance,IndVarName).value = 1
#         Result.lbz.append([None,b,z])
#         for t in instance.TimePeriods:
#           print "Global at",t,"=",instance.posGlobalLoadGenerateMismatch[t].value, \
#                '-',instance.negGlobalLoadGenerateMismatch[t].value,"=",\
#                    instance.GlobalLoadGenerateMismatch[t].value,\
#               "\tDemand =",instance.TotalDemand[t].value, ",",\
#                "Reserve =",instance.ReserveRequirement[t].value
#
#      PrintPRpoints(Result.lbz)
#      return Result
#### end enumeration
########################################################################


      if verbosity > 1:
         print "We have bU =",bU,"...about to free all",IndVarName,"for",len(ScenarioList),"scenarios"

      for scenario in ScenarioList:
         sname = scenario[0]
         instance = ph._instances[sname]
         getattr(instance,IndVarName).fixed = False  # free scenario selection variable
      instance.preprocess() 
      if verbosity > 1: print "\tall",IndVarName,"freed", time.time() - STARTTIME


      if HGdebug > 0:
         lambdaval = (zU-zL)*1000  
         print "solving for lambda =",lambdaval,"( should be enough to yield (1, zU)"
         lagrUtil.Set_ParmValue(ph, multName,lambdaval)
         SolStat, Lagrangian = HGdebugSolve(ph, options, ScenarioList)
         b = Compute_ExpectationforVariable(ph, IndVarName, CCStageNum)
         z = Lagrangian + lambdaval*b
         print "at 160, lambda=",lambdaval,", SolStat =",SolStat," Lagrangian =",Lagrangian,"=",z,"-",lambdaval,"x",b

      Result.lbz = [ [0,bL,zL], [None,bU,zU] ]
      Result.selections = [[], ScenarioList]
      NumIntervals = 1
      if verbosity > 0: 
         print "Initial relative Lagrangian gap =",1-zL/zU,"maxIntervals = ",maxIntervals
         if verbosity > 1: 
            print "entering while loop at ",str(datetime.datetime.now())
         print "\n"
             
############ main loop to search intervals #############
######################################################## 
      while NumIntervals < maxIntervals:
         lapsedTime = time.time() - STARTTIME
         if lapsedTime > maxTime:
            addstatus = '** max time reached ' + str(lapsedTime)
            print addstatus
            Result.status = Result.status + '\n' + addstatus
            break
         if verbosity > 1:
            print "Top of while with",NumIntervals," intervals"
            PrintPRpoints(Result.lbz)
         for i in range(1,len(Result.lbz)):
            if not Result.lbz[i][0] == None: continue
            if verbosity > 1: 
               print "Searching unfathomed interval with upper point =",Result.lbz[i]
            bL = Result.lbz[i-1][1]
            zL = Result.lbz[i-1][2]
            bU = Result.lbz[i][1]
            zU = Result.lbz[i][2]
            lambdaval = (zU - zL) / (bU - bL)
            if verbosity > 1:  
               print "\ti.e., searching for b in ["+str(round(bL,4))+", "+str(round(bU,4))+"] with lambda =",lambdaval
            lagrUtil.Set_ParmValue(ph, multName,lambdaval)

            if verbosity > 0: 
               print "Solve begins with lambda=",lambdaval,str(datetime.datetime.now())
            SolStat, Lagrangian = lagrUtil.solve_ph_code(ph, options)
            if verbosity > 0: 
               print "\tends",str(datetime.datetime.now())
            b = Compute_ExpectationforVariable(ph, IndVarName, CCStageNum)
            z = Lagrangian + lambdaval*b

            Selections = []
            for scenario in ScenarioList:
               instance = ph._instances[scenario[0]]
               if getattr(instance,IndVarName).value == 1: Selections.append(scenario)
            if verbosity > 1: 
               print len(Selections),"selections"
               if verbosity > 2:
                  print "\nMiddle of loop...after solving to obtain (b,z)...Last Result attribute:" 
                  attrResult = inspect.getmembers(Result)
                  print attrResult[len(attrResult)-1][0]
                  print "\n===========================================\n"

            if b < bL or b > bU:
               print "** b < bL =",bL," or b > bU =",bU
               if b < bL - alphaTol or b > bU + alphaTol:
                  addstatus = "\n** Encountered computed probability = "+str(b)+\
                              ", outside search interval ["+str(bL)+", "+str(bU)+"]"
                  Result.status = Result.status + addstatus
                  if verbosity > 0:
                     print addstatus
                     print "\t using lambda =",lambdaval," ?=", (zU-zL)/(bU-bL)
                     print "\t ...check tolerances"
                     PrintPRpoints(Result.lbz)
                  return Result
               if b < bL: b = bL
               if b > bU: b = bU
               print "\t but within alphaTol, so we continue by adjusting b = ",b

# We have bL <= b <= bU (as necessary, at least within tolerance)
            if b <= bL+alphaTol or b >= bU-alphaTol:
# b is within tolerance of an endpoint
               if z <= zL: lambdaval = 0.
               Result.lbz[i][0] = lambdaval
               if verbosity > 0:
                  print "Interval "+str(i)+", ["+str(bL)+", "+str(bU)+\
                    "] fathomed with lambda =",lambdaval
                  print "\tlbz =",Result.lbz[i]
            else:
               Result.lbz = Insert([None,b,z],i,Result.lbz)
               Result.selections = Insert(Selections,i,Result.selections)
               if verbosity > 0:  
                  print "Interval "+str(i)+", ["+str(bL)+", "+str(bU)+ \
                    "] split at ("+str(b)+", "+str(z)+")"

         if len(Result.lbz) == NumIntervals+1: # all intervals fathomed
            if verbosity > 1: print "break with len(lbz) =",len(Result.lbz),\
                " = ",NumIntervals+1
            break
         if NumIntervals >= maxIntervals:
            if verbosity > 0: print "max number of intervals reached...terminating"
            break
# while loop continues 
         NumIntervals = NumIntervals + 1
         if verbosity > 1: PrintPRpoints(Result.lbz)

################ end while loop ###################

      if verbosity > 1:  print "\nend while loop...setting multipliers"
      for i in range(1,len(Result.lbz)):
         db = Result.lbz[i][1] - Result.lbz[i-1][1]
         dz = Result.lbz[i][2] - Result.lbz[i-1][2]
         if dz > 0:
            Result.lbz[i][0] = dz/db
         else:
            print "dz =",dz," at ",i,": ",Result.lbz[i]," -",Result.lbz[i-1]
            Result.lbz[i][0] = 0
      if verbosity > 0: PrintPRpoints(Result.lbz)
      addstatus = '\nLagrange multiplier search ends at '+str(datetime.datetime.now())
      if verbosity > 0: print addstatus," at ",str(datetime.datetime.now())
      Result.status = Result.status + addstatus

      outName = csvPrefix + "PRoptimal.csv"
      outFile = file(outName,'w')
      if verbosity > 0: print "writing PR points to ",outName
      for lbz in Result.lbz: print >>outFile, str(lbz[1])+ ", " +str(lbz[2])
      outFile.close()

      outName = csvPrefix + "OptimalSelections.csv"
      outFile = file(outName,'w')
      if verbosity > 0: print "writing optimal selections for each PR point to ",csvPrefix+'PRoptimal.csv'
      for selections in Result.selections: 
         char = ""
         thisSelection = "" 
         for slist in selections: 
            if slist:
               thisSelection = thisSelection + char + slist[0]
               char = ","
         print >>outFile, thisSelection
      outFile.close()
      if verbosity > 0:  print "\nReturning status:\n",Result.status,"\n=======================\n"
     
################################
      if verbosity > 2:
         print "\nAbout to return...Result attributes:", len(inspect.getmembers(Result))
         for attr in inspect.getmembers(Result): print attr[0]
         print "\n===========================================\n"
# LagrangeParametric ends here
      return Result
################################
      

####################################### start run ####################################

   AllInOne = False
##HG   VERYSTARTTIME=time.time()
##HG   print "##############VERYSTARTTIME:",str(VERYSTARTTIME-VERYSTARTTIME)
   
##########################
# options defined here (re-organized Mar 18)
##########################
   try:
      conf_options_parser = construct_ph_options_parser("lagrange [options]")
      conf_options_parser.add_option("--alpha-min",
                                     help="The min alpha level for the chance constraint. Default is 0",
                                     action="store",
                                     dest="alpha_min",
                                     type="float",
                                     default=0.)
      conf_options_parser.add_option("--alpha-max",
                                     help="The alpha level for the chance constraint. Default is 1.",
                                     action="store",
                                     dest="alpha_max",
                                     type="float",
                                     default=1.)
      conf_options_parser.add_option("--alpha-tol",
                                     help="Tolerance for testing equality to alpha. Default is 1e-5",
                                     action="store",
                                     dest="alpha_tol",
                                     type="float",
                                     default=1e-5)
      conf_options_parser.add_option("--Lagrange-gap",
                                     help="The (relative) Lagrangian gap acceptable for the chance constraint. Default is 10^-4",
                                     action="store",
                                     type="float",
                                     dest="Lagrange_gap",
                                     default=0.0001)  
      conf_options_parser.add_option("--min-prob",
                                     help="Tolerance for testing probability > 0. Default is 1e-9",
                                     action="store",
                                     dest="min_prob",
                                     type="float",
                                     default=1e-5)
      conf_options_parser.add_option("--max-intervals",
                                     help="The max number of intervals generated; if causes termination, non-fathomed intervals have multiplier=None.  Default = 100.",
                                     action="store",
                                     dest="max_intervals",
                                     type="int",
                                     default=100)
      conf_options_parser.add_option("--max-time",
                                     help="Maximum time (seconds). Default is 3600.",
                                     action="store",
                                     dest="max_time",
                                     type="float",
                                     default=3600) 
      conf_options_parser.add_option("--lambda-parm-name",
                                     help="The name of the lambda parameter in the model. Default is lambdaMult",
                                     action="store",
                                     dest="lambda_parm_name",
                                     type="string",
                                     default="lambdaMult")
      conf_options_parser.add_option("--indicator-var-name",
                                     help="The name of the indicator variable for the chance constraint. The default is delta",
                                     action="store",
                                     dest="indicator_var_name",
                                     type="string",
                                     default="delta")
      conf_options_parser.add_option("--stage-num",
                                     help="The stage number of the CC indicator variable (number, not name). Default is 2",
                                     action="store",
                                     dest="stage_num",
                                     type="int",
                                     default=2)
      conf_options_parser.add_option("--csvPrefix",
                                     help="Output file name.  Default is ''",
                                     action="store",
                                     dest="csvPrefix",
                                     type="string",
                                     default='')
      conf_options_parser.add_option("--verbosity",
                                     help="verbosity=0 is no extra output, =1 is medium, =2 is debug, =3 super-debug. Default is 1.",
                                     action="store",
                                     dest="verbosity",
                                     type="int",
                                     default=1)
# The following needed for solve_ph_code in lagrangeutils
      conf_options_parser.add_option("--solve-with-ph",
                                     help="Perform solves via PH rather than an EF solve. Default is False",
                                     action="store_true",
                                     dest="solve_with_ph",
                                     default=False)
##HG: deleted params filed as deletedParam.py
#######################################################################################################

      (options, args) = conf_options_parser.parse_args(args=args)
   except SystemExit:
      # the parser throws a system exit if "-h" is specified - catch
      # it to exit gracefully.
      return

   # create the reference instances and the scenario tree - no scenario instances yet.
   if options.verbosity > 0: print "Loading reference model and scenario tree"
   reference_model, full_scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory = load_models(options)
   if (reference_model is None) or (full_scenario_tree is None) or (scenario_tree_instance is None):
      raise RuntimeError, "***ERROR: Failed to initialize reference model/instance pair and/or the scenario tree."

########## Here is where multiplier search is called from run() ############
   Result = LagrangeParametric()
##################################################################################### 
   if options.verbosity > 0: 
      print "\n===========================================\n"
      print "\nreturned from LagrangeParametric"
      if options.verbosity > 2:
         print "\nFrom run, Result should have status and ph objects..."
         for attr in inspect.getmembers(Result): print attr
         print "\n===========================================\n"
   
   try:
     status = Result.status
     print "status =",Result.status
   except:
     print "status not defined"
     sys.exit()

   try:
      lbz = Result.lbz
      PrintPRpoints(lbz)
      outFile = file(options.csvPrefix+"PRoptimal.csv",'w')
      for lbz in Result.lbz: print >>outFile, str(lbz[1])+ ", " +str(lbz[2])
      outFile.close()
   except:
      print "Result.lbz not defined"
      sys.exit()

   try:
      ScenarioList = Result.ScenarioList
      ScenarioList.sort(key=operator.itemgetter(1))   
      outFile = file(options.csvPrefix+"ScenarioList.csv",'w')
      for scenario in ScenarioList: print >>outFile, scenario[0]+", "+str(scenario[1])
      outFile.close()
   except:
      print "Result.ScenarioList not defined"
      sys.exit()

##HG Mar 20: deleted morePR from this program...run separately as lagrangeMorePR.py

########################### run ends here ##############################

########## begin function definitions ################
def Compute_ExpectationforVariable(ph, IndVarName, CCStageNum):
   SumSoFar = 0.0
   node_probability = 0.0
   stage = ph._scenario_tree._stages[CCStageNum-1]
   for tree_node in stage._tree_nodes:
      for scenario in tree_node._scenarios:
         instance = ph._instances[scenario._name]
         #print "scenario._probability:",scenario._probability
         node_probability += scenario._probability
         #print "node_probability:",node_probability
         #print "getattr(instance, IndVarName).value:",getattr(instance, IndVarName).value
         SumSoFar += scenario._probability * getattr(instance, IndVarName).value
         #print "SumSoFar:",SumSoFar
   return SumSoFar / node_probability

#######################################

def Insert(newpoint,location,List):
    newList = []
    for i in range(location): newList.append(List[i])
    newList.append(newpoint)
    for i in range(location,len(List)): newList.append(List[i])
    return newList

#######################################

def ismember(List,member):  # designed to test 1st member of each list in List (ie, 1st column)
   for i in List:
      if len(i[0]) == 0: continue   # in case list contains empty list
      if i[0] == member: return True
   return

#######################################

def putcommas(num):  
   snum = str(num)
   decimal = snum.find('.')
   if decimal >= 0:
      frac = snum[decimal:]
      snum = snum[0:decimal]
   else: frac = ''
   if len(snum) < 4: return snum + frac
   else: return putcommas(snum[:len(snum)-3]) + "," + snum[len(snum)-3:len(snum)] + frac

#######################################

def HGdebugSolve(ph,options,ScenarioList):
   print "HGdebugSolve prints attributes after solving" 
   SolStat, Lagrangian = lagrUtil.solve_ph_code(ph, options)
   IndVarName = options.indicator_var_name
   for scenario in ScenarioList:
       sname = scenario[0]
       instance = ph._instances[sname]
       if getattr(instance,IndVarName).fixed: stat = "fixed"
       else: stat = "free"
       lambdaval = getattr(instance, options.lambda_parm_name).value
       print IndVarName+"("+sname+") =",getattr(instance,IndVarName).value, stat, "\tlambda =",lambdaval
   b = Compute_ExpectationforVariable(ph, IndVarName, options.stage_num)
   z = Lagrangian + lambdaval*b
   print "L = ",z," - ",lambdaval,"x",b
   return SolStat, Lagrangian

def PrintPRpoints(PRlist):
   if len(PRlist) == 0: 
      print "No PR points"
   else:
      print len(PRlist),"PR points:"
      blanks = "                      "
      print "            lambda        beta-probability       min cost "
      for row in PRlist:
         b = round(row[1],4)
         z = round(row[2])
# lambda = row[0] could be float, string, or None
         sl = str(row[0])
         sl = blanks[0:20-len(sl)] + sl
         sb = str(b)
         sb = blanks[0:20-len(sb)] + sb
         sz = putcommas(z)
         sz = blanks[2:20-len(sz)] + sz
         print sl+" "+sb+" "+sz
      print "==================================================================\n"
   return

###########
def ZeroOneIndexListsforVariable(ph, IndVarName, CCStageNum):
   # return lists across scenarios of the zero value scenarios and one value scenarios
   # for unindexed variable in the ph object for a stage (one based)
   # in this routine we trust that it is binary
   ZerosList = []
   OnesList = []

   stage = ph._scenario_tree._stages[CCStageNum-1]
   for tree_node in stage._tree_nodes:
      for scenario in tree_node._scenarios:
         instance = ph._instances[scenario._name]
         locval = getattr(instance, IndVarName).value 
         #print locval
         if locval < 0.5:
            ZerosList.append(scenario)
         else:
            OnesList.append(scenario)
   return [ZerosList,OnesList]

###########
def PrintanIndexList(IndList):
   # show some useful information about an index list (note: indexes are scenarios)
   print "Zeros:"
   for i in IndList[0]:
      print i._name
   print "Ones:"
   for i in IndList[1]:
      print i._name

###########
def ReturnIndexListNames(IndList):
   ListNames=[[],[]]
   #print "Zeros:"
   for i in IndList[0]:
      ListNames[0].append(i._name)
   #print "Ones:"
   for i in IndList[1]:
      ListNames[1].append(i._name)
   return ListNames

#
# the main script routine starts here
#

if __name__ == "__main__":

   run()

# RESTORE THE BELOW ASAP
#try:
#    run()
#except ValueError, str:
#    print "VALUE ERROR:"
#    print str
#except IOError, str:
#    print "IO ERROR:"
#    print str
#except pyutilib.common.ApplicationError, str:
#    print "APPLICATION ERROR:"
#    print str
#except RuntimeError, str:
#    print "RUN-TIME ERROR:"
##    print str
#except:
#   print "Encountered unhandled exception", sys.exc_info()[0]
#   traceback.print_exc()   
   
   
