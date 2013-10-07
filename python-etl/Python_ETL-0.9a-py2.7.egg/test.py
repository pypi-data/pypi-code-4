import sys
sys.path.append(r'C:\Users\jugovich-michael\workspace\pythonetl')
import cardsharp as cs
from cardsharp.test import test_common_tasks
from cardsharp.test.transform import test_metadata
import time
#test_rules.test_load_length()
import cardsharp as cs
from cardsharp.transform import * 
#test_common_tasks.test_find_max_variable_lengths()
def func(row):
    print row
    time.sleep(1)

#RT1 = RuleTask(3, func)
#RT2 = RuleTask(1, func)
#RT3 = RuleTask(2, func)
#RTs = [RT1, RT2, RT3]
#RTM = RuleTaskManager(RTs)

#ds = cs.Dataset('abc')
#for x in range(100):
#    ds.add_row([str(x),str(x+1),str(x+2)])
#
##ds.transform(RTM)
#
#print 'a' in ds.variables
from datetime import datetime

#test_metadata.TestRuleMetadata()
print 'complete @ %s.' % datetime.now().isoformat(' ')
#ds = cs.load(source='dev_cchr', dataset='arrestx', user='root', pwd='pass', 
#             format='mysql', where='casenumx=3')
#ds_1 = cs.load(source='dev_cchr', dataset='arrestx', user='root', pwd='pass', 
#             format='mysql', where='astate=10', as_cache=True, cache_key = ['cycnumx'])
#cs.wait()
#print 'complete @ %s.' % datetime.now().isoformat(' ')
#ds_info = cs.load(source='dev_cchr', dataset='arrestx', user='root', pwd='pass', format='mysql', as_cache=True, 
#                  cache_key = ['casenum', 'cycnum'], select=['casenum', 'cycnum', 'afed', 'astate'])

#ds = cs.Dataset('abc')
#ds.add_row(['', ' ', None])
#ds_1 = cs.load(source=r'C:\Users\jugovich-michael\workspace\bjs_rules\logs\achgsvr_wvfbi_0.txt', format='text',
#               var_names=[('segment', 'integer'), ('variable', 'integer'), 
#                               ('phase', 'integer'), ('id', 'integer'), 'convert_state', 
#                               'convert_key', 'error_message', 'convert_time'])
#for row in ds_1:
    #print row
ds1 = cs.load(source='dev_cchr', dataset='arrestx', user='root', pwd='pass', format='mysql')
ds2 = cs.load(source='dev_cchr', dataset='sentencex', user='root', pwd='pass', format='mysql')
ds1.save(source=r'P:\6684\Common\bjs\data\temp_out\arrestx.sav', format='spss')
ds2.save(source=r'P:\6684\Common\bjs\data\temp_out\sentencex.sav', format='spss')



#print cs.variables.VariableSet(['a', 'b', ('c', 'integer')])
#ds = cs.Dataset('abc')
#ds.save(source='dev_cchr', dataset='test', user='root', pwd='pass', format='mysql')
#for row in ds:
#    print row


#ds = cs.load(source=r'C:\Users\jugovich-michael\workspace\bjs_rules\logs\diff_single_snttextx.txt',
#             format='text', delimiter='\t', var_names=['segment', 'variable', 'phase', 'state', 'set14_snttext', 'set7_snttext', 'casenum', 'cycnum', 'cseqnum', 'new_val', 'time', 'new'])
#ds_1 = cs.load(source=r'C:\Users\jugovich-michael\workspace\bjs_rules\logs\diff_single_new_vals_snttextx.txt',
#             format='text', delimiter='\t', var_names=['segment', 'variable', 'phase', 'set14_snttext', 'time', 'new'])
#cs.wait()
#ds.save(source=r'C:\Users\jugovich-michael\workspace\bjs_rules\logs\diff_snttextx.xls',
#             format='excel', drop=['new', 'time'], overwrite=True )
#ds_1.save(source=r'C:\Users\jugovich-michael\workspace\bjs_rules\logs\diff_single_new_vals_snttextx.xls',
#             format='excel', drop=['new', 'time'], overwrite=True )
#ds = cs.load(source='dev_cchr', dataset='standard_reports', user='root', 
#             pwd='pass', format='mysql')
#cs.wait()
#ds.save(source='standard_reports', format='mongo')

#from cardsharp import rules
#
#d = cs.Dataset('abc')
#
#d.variables['a'].rules.length = 1
#cs.wait()
#
#try:
#    d.add_row(['as', 'd', 'd'])
#except rules.RuleError as e:
#    print e
#
#ds = cs.load(source='dev_cchr', dataset='standard_reports', user='root', 
#             pwd='pass', format='mysql')
#
#
#for row in ds:
#    print row
#
#
#ds = cs.load(source='C:\Users\jugovich-michael\workspace\demo\data\input.txt',
#                 format = 'text', delimiter = '|')
#
#for row in ds:
#    print row