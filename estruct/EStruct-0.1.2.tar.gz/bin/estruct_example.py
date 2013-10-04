#!/usr/bin/env python
from estruct.estruct import EStruct, StructObject

def run_example(name, testdata, struct_params, local={}):
    print "="*80
    print "Test:", name
    print "Test data:", testdata
    print "EStruct:", struct_params 
    print "-"*80
    teststring= "".join([chr(x) for x in testdata])
    
    s=EStruct(*struct_params)
    r1=s.unpack(teststring, **local)
    print "Unpack:",r1
    values=tuple([getattr(r1,v) for v in r1.__dict__])
    packed_result=s.pack(*values, **local)   
    print "Pack:",packed_result.encode('hex')
    print "Result:", (packed_result==teststring)
    print "-"*80,'\n'
        

if __name__ == "__main__":
    
    f=StructObject("f1 f2.a1 f2.a2 f3.a1.b1 f3.a1.b2 f3.a2")
    print f
    print f.Fields
    
    try:
        sf=f.SubFields("Balls to you!")
    except KeyError as ex:
        print "Expected exception raised!", ex
    
    sf=f.SubFields("f1")
    print sf
    sf=f.SubFields("f2")
    print sf
    sf=f.SubFields("f3")    
    print sf
    print sf.__repr__()
    
    obj=f.CreateInstance("obj",1,(2,3),((4,5),6))
    print obj
    
    
    run_example("Conditional with True result", 
            [0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0], 
            ('Test','f1 f2 f3','!II(f1==1?Q|I)'))
    
    run_example("Conditional with False result", 
            [0,0,0,0,0,0,0,2,0,0,0,1], 
            ('Test','f1 f2 f3','!II(f1==1?Q|I)'))
    
    run_example("Conditional with True result (Empty false)", 
            [0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0], 
            ('Test','f1 f2 f3','!II(f1==1?Q|)'))
    
    run_example("Conditional with False result (Empty false)", 
            [0,0,0,0,0,0,0,2], 
            ('Test','f1 f2 f3','!II(f1==1?Q|)'))
      
    run_example("Conditional with True result (Empty true)", 
            [0,0,0,1,0,0,0,2], 
            ('Test','f1 f2 f3','!II(f1==1?|Q)'))
      
    run_example("Conditional with False result (Empty true)", 
            [0,0,0,0,0,0,0,2,0,0,0,1,0,0,0,0], 
            ('Test','f1 f2 f3','!II(f1==1?|Q)'))
      
    run_example("Nested conditional with False result outer true - inner false", 
            [0,0,0,1,0,0,0,2], 
            ('Test','f1 f2 f3','!II(f1==1?(f2==3?3s|)|Q)'))

    run_example("Nested conditional with False result outer true - inner true", 
            [0,0,0,1,0,0,0,3,ord('p'),ord('o'),ord('p')], 
            ('Test','f1 f2 f3','!II(f1==1?(f2==3?3s|)|Q)'))

    run_example("Nested conditional with False result outer false", 
            [0,0,0,0,0,0,0,3,0,0,0,1,0,0,0,2], 
            ('Test','f1 f2 f3','!II(f1==1?(f2==3?3s|)|Q)'))
             
    run_example("Fixed size array",
            [0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1],
            ('Test','f1.a f1.b','!8[IQ]'))
    
    run_example("Fixed size array (of conditionals)",
        [1,0,0,0,1,0,0,0,2,0,0,0,8,
        0,0,0,2,0,0,0,2,0,0,0,7,
        0,0,0,3,0,0,0,2,0,0,0,6,
        0,0,0,4,0,0,0,2,0,0,0,5,
        0,0,0,0,5,0,0,2,0,0,0,4,
        0,0,0,0,6,0,0,2,0,0,0,3,
        0,0,0,0,7,0,0,2,0,0,0,2,
        0,0,0,0,8,0,0,2,0,0,0,1],
        ('Test','f0 f1.a f1.b','!B8[I(f0==1?Q|)]'))
    
    run_example("Unknown size array",
            [0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1],
            ('Test','f1.a f1.b','![IQ]'))
    
    run_example("Unknown size array with prefixed struct",
            [1,2,6,9,ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1],
            ('Test','f01 f02 f03 f04 f1.a f1.b','!2bh4s[IQ]'))

    run_example("Unknown size array with prefixed struct - no fields in array",
            [ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1],
            ('Test','f01 f1','!4s[I]'))
    
    run_example("Use an external value in condition",
            [0,0,0,8,0,0,0,2,0,0,0,1],
            ('Test','f1 f2','!(testval==1?iQ|)'),local={"testval":True})
  
    run_example("Unknown sized array of chars",
            [0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51],
            ('Test','f1','![c]'))
      
    run_example("Array of ints followed by Unknown sized array of chars",
            [0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51],
            ('Test','f3 f4','!3[I][c]'))
    
    run_example("Empty array (char)",
            [],
            ('Test','f1','![c]'))
    
    run_example("Evaluated count", 
            [0,0,0,3,0,0,0,2,0,0,0,1,0,0,0,0], 
            ('Test','f1 f2','!I{f1}[I]'))
    
    run_example("Evaluated count - complex evaluation", 
            [0,0,0,3,
             0,0,0,2,ord('a'),ord('b'),
             0,0,0,1,ord('c'),
             0,0,0,4,ord('d'),ord('o'),ord('g'),ord(' ')], 
            ('Test','f1 f2.a1 f2.a2','!I{f1}[I{f2[INDEX].a1}[c]]'))
      
 