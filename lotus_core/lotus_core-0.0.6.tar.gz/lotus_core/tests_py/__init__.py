

import test1
import test2
import test3
import test4
import test5
import test6
import test7
import test8
import test9


def do_test(no):
  if no==1: test1.run_test()
  if no==2: test2.run_test()
  if no==3: test3.run_test()
  if no==4: test4.run_test()
  if no==5: test5.run_test()
  if no==6: test6.run_test()
  if no==7: test7.run_test()
  if no==8: test8.run_test()
  if no==9: test9.run_test()

def self_tests(li):
  for no in li:
    do_test(no)

def self_tests_all():
  li = [1, 2, 3, 4, 5, 6, 7, 8, 9]
  self_tests(li) 


