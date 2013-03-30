#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python tests originally created or extracted from other peoples work. The
#     parts were too small to be protected.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

print "List contraction on the module level:"
x = [(u if u%2==0 else 0) for u in range(10)]
print x

print "List contraction on the function level:"
def someFunction():
   x = [(u if u%2==0 else 0) for u in range(10)]
   print x

someFunction()

print "List contractions with no, 1 one 2 conditions:"
def otherFunction():
    print [ x for x in range(8) ]
    print [ x for x in range(8) if x % 2 == 1 ]
    print [ x for x in range(8) if x % 2 == 1 if x > 4 ]

otherFunction()

print "Complex list contractions with more than one for:"
def complexContractions():
   print [ (x,y) for x in range(3) for y in range(5) ]

   seq = range(3)
   res = [(i, j, k) for i in iter(seq) for j in iter(seq) for k in iter(seq)]

   print res

complexContractions()

print "Contraction for 2 fors and one final if refering to first for:"

def trickyContraction():
   class Range:
      def __init__( self, value ):
         self.value = value

      def __iter__( self ):
         print "Giving range iter to", self.value

         return iter( range( self.value ))

   def Cond( y ):
      print "Checking against", y

      return y == 1

   r = [ (x,z,y) for x in Range(3) for z in Range(2) for y in Range(4) if Cond(y) ]
   print "result", r

trickyContraction()

def lambdaWithcontraction( x ):
   l = lambda x : [ z for z in range(x) ]
   r = l(x)
   print locals()

lambdaWithcontraction( 3 )
