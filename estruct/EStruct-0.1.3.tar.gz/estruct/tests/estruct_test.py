from estruct.estruct import EStruct, StructObject 
import unittest

class StructObjectTestCase(unittest.TestCase):
    def setUp(self):
        self.struct_object=StructObject("f1 f2.a1 f2.a2 f3.a1.b1 f3.a1.b2 f3.a2")

    def tearDown(self):
        del self.struct_object

    def test___str__(self):
        self.assertEqual(str(self.struct_object), 
                         "f1 f2.a1 f2.a2 f3.a1.b1 f3.a1.b2 f3.a2",
                         'incorrect str string')

    def test___repr__(self):
        self.assertEqual(repr(self.struct_object), 
                         'StructObject("f1 f2.a1 f2.a2 f3.a1.b1 f3.a1.b2 f3.a2")',
                         'incorrect repr string: {}'.format(repr(self.struct_object)))
        
    def test_fields(self):
        self.assertEqual(self.struct_object.Fields, 
                         ['f1','f2','f3'],
                         'incorrect Fields')
   
    def test_nodes(self):
        self.assertEqual(self.struct_object.Nodes, 
                         ['f1','f2.a1', 'f2.a2','f3.a1.b1','f3.a1.b2','f3.a2'],
                         'incorrect Nodes: {}'.format(self.struct_object.Nodes))    
            
    def test_sub_fields_invalid_field(self):
        self.assertRaises(KeyError, self.struct_object.SubFields, ("invalidField",))
        
    def test_sub_fields(self):
        sf=self.struct_object.SubFields("f1")
        self.assertEqual(sf, None, 'Should have no sub fields so expecting None')
        
        sf=self.struct_object.SubFields("f2")
        self.assertEqual(type(sf), StructObject, 'Should be of type StructObject') 
        self.assertEqual(sf.Fields, ['a1','a2'], 'incorrect fields in subfield: {}'.format(sf.Fields)) 
        a1_sf=sf.SubFields("a1")
        self.assertEqual(a1_sf, None, 'Should have no sub fields so expecting None')
        a2_sf=sf.SubFields("a2")
        self.assertEqual(a2_sf, None, 'Should have no sub fields so expecting None')
        
        sf=self.struct_object.SubFields("f3")
        self.assertEqual(type(sf), StructObject, 'Should be of type StructObject')
        self.assertEqual(sf.Fields, ['a1','a2'], 'incorrect fields in subfield: {}'.format(sf.Fields)) 
        a1_sf=sf.SubFields("a1")
        self.assertEqual(type(a1_sf), StructObject, 'Should be of type StructObject') 
        self.assertEqual(a1_sf.Fields, ['b1','b2'], 'incorrect fields in subfield: {}'.format(sf.Fields))        
        b1_sf=a1_sf.SubFields("b1")
        self.assertEqual(b1_sf, None, 'Should have no sub fields so expecting None')
        b2_sf=a1_sf.SubFields("b2")
        self.assertEqual(b2_sf, None, 'Should have no sub fields so expecting None')
        a2_sf=sf.SubFields("a2")
        self.assertEqual(a2_sf, None, 'Should have no sub fields so expecting None')
       
    def test_create_instance(self):
        obj=self.struct_object.CreateInstance("obj",1,(2,3),((4,5),6))
        self.assertEqual(obj.__class__.__name__, "obj", "incorrect object name")
        self.assertEqual(obj._fields, ("f1","f2","f3"), "incorrect fields")
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2.a1, 2, "incorrect value: {}".format(obj.f2.a1))
        self.assertEqual(obj.f2.a2, 3, "incorrect value: {}".format(obj.f2.a2))
        self.assertEqual(obj.f3.a1.b1, 4, "incorrect value: {}".format(obj.f3.a1.b1))
        self.assertEqual(obj.f3.a1.b2, 5, "incorrect value: {}".format(obj.f3.a1.b2))
        self.assertEqual(obj.f3.a2, 6, "incorrect value: {}".format(obj.f3.a2))        

        
class EStructConditionalTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3','!II(f1==1?Q|I)')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 0x0000000100000000, "incorrect value: {}".format(obj.f3))

        data=[0,0,0,0,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 0x00000001, "incorrect value: {}".format(obj.f3))

    def test_packing(self):
        packed_result=self.struct.pack(1,2,0x0000000100000000)
        data=[0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(0,2,1)
        data=[0,0,0,0,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))        

class EStructConditionalEmptyTrueTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3','!II(f1==1?|Q)')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, None, "incorrect value: {}".format(obj.f3))

        data=[0,0,0,0,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 0x0000000100000000, "incorrect value: {}".format(obj.f3))

    def test_packing(self):
        packed_result=self.struct.pack(1,2,None)
        data=[0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(0,2,0x0000000100000000)
        data=[0,0,0,0,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  

class EStructConditionalEmptyFalseTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3','!II(f1==1?Q|)')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 0x0000000100000000, "incorrect value: {}".format(obj.f3))

        data=[0,0,0,0,0,0,0,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, None, "incorrect value: {}".format(obj.f3))

    def test_packing(self):
        packed_result=self.struct.pack(1,2,0x0000000100000000)
        data=[0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(0,2,None)
        data=[0,0,0,0,0,0,0,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  

class EStructNestedConditionalTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3','!II(f1==1?(f2==3?3s|)|Q)')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, None, "incorrect value: {}".format(obj.f3))

        data=[0,0,0,1,0,0,0,3,ord('p'),ord('o'),ord('p')]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 3, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 'pop', "incorrect value: {}".format(obj.f3))

        data=[0,0,0,0,0,0,0,3,0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 3, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 0x0000000100000002, "incorrect value: {}".format(obj.f3))
        
    def test_packing(self):
        packed_result=self.struct.pack(1,2,None)
        data=[0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(1,3,'pop')
        data=[0,0,0,1,0,0,0,3,ord('p'),ord('o'),ord('p')]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  

        packed_result=self.struct.pack(0,3,0x0000000100000002)
        data=[0,0,0,0,0,0,0,3,0,0,0,1,0,0,0,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  
        
class EStructConditionalConsumeFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3 f4','!I(f1==1?2|QI)B')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, None, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, None, "incorrect value: {}".format(obj.f3))
        self.assertEqual(obj.f4, 2, "incorrect value: {}".format(obj.f4))

        data=[0,0,0,0,0,0,0,2,0,0,0,3,0,0,0,4,2]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 0x200000003, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 4, "incorrect value: {}".format(obj.f3))
        self.assertEqual(obj.f4, 2, "incorrect value: {}".format(obj.f4))
        
    def test_packing(self):
        packed_result=self.struct.pack(1,None,None,2)
        data=[0,0,0,1,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(0,0x0000000200000003,4,2)
        data=[0,0,0,0,0,0,0,2,0,0,0,3,0,0,0,4,2]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  
                
class EStructNestedConditionalConsumeFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2 f3 f4 f5','!I(f1==1?I2|I(f2==1?2I|I1))B')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2,5]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 1, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, None, "incorrect value: {}".format(obj.f3))
        self.assertEqual(obj.f4, None, "incorrect value: {}".format(obj.f4))
        self.assertEqual(obj.f5, 5, "incorrect value: {}".format(obj.f5))

        data=[0,0,0,0,0,0,0,1,0,0,0,3,0,0,0,4,5]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 1, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 3, "incorrect value: {}".format(obj.f3))
        self.assertEqual(obj.f4, 4, "incorrect value: {}".format(obj.f4))
        self.assertEqual(obj.f5, 5, "incorrect value: {}".format(obj.f5))
        
        data=[0,0,0,0,0,0,0,2,0,0,0,3,5]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, 0, "incorrect value: {}".format(obj.f1))
        self.assertEqual(obj.f2, 2, "incorrect value: {}".format(obj.f2))
        self.assertEqual(obj.f3, 3, "incorrect value: {}".format(obj.f3))
        self.assertEqual(obj.f4, None, "incorrect value: {}".format(obj.f4))
        self.assertEqual(obj.f5, 5, "incorrect value: {}".format(obj.f5))        

    def test_packing(self):
        packed_result=self.struct.pack(1,2,None,None,5)
        data=[0,0,0,1,0,0,0,2,5]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
        packed_result=self.struct.pack(0,1,3,4,5)
        data=[0,0,0,0,0,0,0,1,0,0,0,3,0,0,0,4,5]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))  

        packed_result=self.struct.pack(0,2,3,None,5)
        data=[0,0,0,0,0,0,0,2,0,0,0,3,5]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex"))) 
        
class EStructEmptyArrayTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1','![c]')

    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual(obj.f1, [], "incorrect value: {}".format(obj.f1))
        
    def test_packing(self):
        packed_result=self.struct.pack([])
        data=[]
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))
        
class EStructFixedSizeArrayTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1.a f1.b','!8[IQ]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( len(obj.f1), 8, "incorrect size: {}".format(len(obj.f1)))
        for i in range(8):
            self.assertEqual(obj.f1[i].a, i+1, "incorrect value: {}".format(obj.f1[i].a))
            self.assertEqual(obj.f1[i].b, 0x200000000+(8-i), "incorrect value: {}".format(obj.f1[i].b))
                    
    def test_packing(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        testdata=[(1,0x200000008),(2,0x200000007),(3,0x200000006),(4,0x200000005),(5,0x200000004),(6,0x200000003),(7,0x200000002),(8,0x200000001)]
        packed_result=self.struct.pack(testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))        


    
class EStructFixedSizeArrayOfConditionalsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f0 f1.a f1.b','!B8[I(f0==1?Q|)]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[1,0,0,0,1,0,0,0,2,0,0,0,8,
                0,0,0,2,0,0,0,2,0,0,0,7,
                0,0,0,3,0,0,0,2,0,0,0,6,
                0,0,0,4,0,0,0,2,0,0,0,5,
                0,0,0,5,0,0,0,2,0,0,0,4,
                0,0,0,6,0,0,0,2,0,0,0,3,
                0,0,0,7,0,0,0,2,0,0,0,2,
                0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( obj.f0, 1, "incorrect value: {}".format(obj.f0))
        self.assertEqual( len(obj.f1), 8, "incorrect size: {}".format(len(obj.f1)))
        for i in range(8):
            self.assertEqual(obj.f1[i].a, i+1, "incorrect value: {}".format(obj.f1[i].a))
            self.assertEqual(obj.f1[i].b, 0x200000000+(8-i), "incorrect value: {}".format(obj.f1[i].b))
                  
        data=[3]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( obj.f0, 3, "incorrect value: {}".format(obj.f0))
        self.assertEqual( len(obj.f1), 0, "incorrect size: {}".format(len(obj.f1)))
                    
    def test_packing(self):
        data=[1,0,0,0,1,0,0,0,2,0,0,0,8,
                0,0,0,2,0,0,0,2,0,0,0,7,
                0,0,0,3,0,0,0,2,0,0,0,6,
                0,0,0,4,0,0,0,2,0,0,0,5,
                0,0,0,5,0,0,0,2,0,0,0,4,
                0,0,0,6,0,0,0,2,0,0,0,3,
                0,0,0,7,0,0,0,2,0,0,0,2,
                0,0,0,8,0,0,0,2,0,0,0,1]
        testdata=[(1,0x200000008),(2,0x200000007),(3,0x200000006),(4,0x200000005),(5,0x200000004),(6,0x200000003),(7,0x200000002),(8,0x200000001)]
        packed_result=self.struct.pack(1,testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex"))) 
        
        data=[3,0,0,0,1,
                0,0,0,2,
                0,0,0,3,
                0,0,0,4,
                0,0,0,5,
                0,0,0,6,
                0,0,0,7,
                0,0,0,8]
        testdata=[(1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,)]
        packed_result=self.struct.pack(3,testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex")))        
  
      
class EStructUnkwnownSizeArrayTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1.a f1.b','![IQ]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( len(obj.f1), 8, "incorrect size: {}".format(len(obj.f1)))
        for i in range(8):
            self.assertEqual(obj.f1[i].a, i+1, "incorrect value: {}".format(obj.f1[i].a))
            self.assertEqual(obj.f1[i].b, 0x200000000+(8-i), "incorrect value: {}".format(obj.f1[i].b))
                  
                    
    def test_packing(self):
        data=[0,0,0,1,0,0,0,2,0,0,0,8,
                0,0,0,2,0,0,0,2,0,0,0,7,
                0,0,0,3,0,0,0,2,0,0,0,6,
                0,0,0,4,0,0,0,2,0,0,0,5,
                0,0,0,5,0,0,0,2,0,0,0,4,
                0,0,0,6,0,0,0,2,0,0,0,3,
                0,0,0,7,0,0,0,2,0,0,0,2,
                0,0,0,8,0,0,0,2,0,0,0,1]
        testdata=[(1,0x200000008),(2,0x200000007),(3,0x200000006),(4,0x200000005),(5,0x200000004),(6,0x200000003),(7,0x200000002),(8,0x200000001)]
        packed_result=self.struct.pack(testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex"))) 
              
class EStructUnkwnownSizeArrayPrefixedStructTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f01 f02 f03 f04 f1.a f1.b','!2bh4s[IQ]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[1,2,6,9,ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( obj.f01, 1, "incorrect value: {}".format(obj.f01))
        self.assertEqual( obj.f02, 2, "incorrect value: {}".format(obj.f02))
        self.assertEqual( obj.f03, 1545, "incorrect value: {}".format(obj.f03))
        self.assertEqual( obj.f04, 'abcd', "incorrect value: {}".format(obj.f04))
                          

        self.assertEqual( len(obj.f1), 8, "incorrect size: {}".format(len(obj.f1)))
        for i in range(8):
            self.assertEqual(obj.f1[i].a, i+1, "incorrect value: {}".format(obj.f1[i].a))
            self.assertEqual(obj.f1[i].b, 0x200000000+(8-i), "incorrect value: {}".format(obj.f1[i].b))
                  
                    
    def test_packing(self):
        data=[1,2,6,9,ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        testdata=[(1,0x200000008),(2,0x200000007),(3,0x200000006),(4,0x200000005),(5,0x200000004),(6,0x200000003),(7,0x200000002),(8,0x200000001)]
        packed_result=self.struct.pack(1,2,1545,'abcd',testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex"))) 

class EStructUnkwnownSizeArrayPrefixedStructNoArrayFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f01 f1','!4s[I]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        self.assertEqual( obj.f01, 'abcd', "incorrect value: {}".format(obj.f01))
        self.assertEqual( len(obj.f1), 24, "incorrect size: {}".format(len(obj.f1)))
        for i in range(8):
            self.assertEqual(obj.f1[i*3], i+1, "incorrect value: {}".format(obj.f1[i*3]))
            self.assertEqual(obj.f1[i*3+1], 2, "incorrect value: {}".format(obj.f1[i*3+1]))
            self.assertEqual(obj.f1[i*3+2], 8-i, "incorrect value: {}".format(obj.f1[i*3+2]))            
                  
                    
    def test_packing(self):
        data=[ord('a'),ord('b'), ord('c'), ord('d'),
            0,0,0,1,0,0,0,2,0,0,0,8,
            0,0,0,2,0,0,0,2,0,0,0,7,
            0,0,0,3,0,0,0,2,0,0,0,6,
            0,0,0,4,0,0,0,2,0,0,0,5,
            0,0,0,5,0,0,0,2,0,0,0,4,
            0,0,0,6,0,0,0,2,0,0,0,3,
            0,0,0,7,0,0,0,2,0,0,0,2,
            0,0,0,8,0,0,0,2,0,0,0,1]
        testdata=[1,2,8,2,2,7,3,2,6,4,2,5,5,2,4,6,2,3,7,2,2,8,2,1]
        packed_result=self.struct.pack('abcd',testdata)
        data_str="".join([chr(x) for x in data])
        self.assertEqual(packed_result,data_str,"Invalid packing - {}".format(packed_result.encode("hex"))) 

class EStructUnkwnownSizeArrayCharsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1','![c]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        
        expected_data=[chr(x) for x in data]
        self.assertEqual( obj.f1, expected_data, "incorrect value: {}".format(obj.f1))
                    
    def test_packing(self):
        data=[0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51]
        testdata=[chr(x) for x in data]
        packed_result=self.struct.pack(testdata)
        expected_data="".join([chr(x) for x in data])
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 

class EStructArrayOfIntsFollowedByUnkwnownSizeArrayCharsTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2','!3[I][c]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        
        self.assertEqual( obj.f1[0], 2, "incorrect value: {}".format(obj.f1[0]))
        self.assertEqual( obj.f1[1], 3, "incorrect value: {}".format(obj.f1[1]))
        self.assertEqual( obj.f1[2], 4, "incorrect value: {}".format(obj.f1[2]))

        expected_data=[chr(x) for x in data[12:]]
        self.assertEqual( obj.f2, expected_data, "incorrect value: {}".format(obj.f1))
                    
    def test_packing(self):
        data=[0,0,0,2,0,0,0,3,0,0,0,4,49,50,50,52,50,50,50,51]
        expected_data="".join([chr(x) for x in data])

        testdata=[chr(x) for x in data[12:]]
        packed_result=self.struct.pack([2,3,4],testdata)
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 


class EStructExternalValueInConditionTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2','!(testval==1?iQ|)')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,8,0,0,0,2,0,0,0,1]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str, testval=True)
        
        self.assertEqual( obj.f1, 8, "incorrect value: {}".format(obj.f1))
        self.assertEqual( obj.f2, 0x200000001, "incorrect value: {}".format(obj.f2))
        
        data=[]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str, testval=False)
        
        self.assertEqual( obj.f1, None, "incorrect value: {}".format(obj.f1))
        self.assertEqual( obj.f2, None, "incorrect value: {}".format(obj.f2))
                            
    def test_packing(self):
        data=[0,0,0,8,0,0,0,2,0,0,0,1]
        expected_data="".join([chr(x) for x in data])

        packed_result=self.struct.pack(8,0x200000001, testval=True)
        
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 

        data=[]
        expected_data="".join([chr(x) for x in data])

        packed_result=self.struct.pack(None,None, testval=False)
        
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 


class EStructEvaluatedCountTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2','!I{f1}[I]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,3,0,0,0,2,0,0,0,1,0,0,0,0]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        
        self.assertEqual( obj.f1, 3, "incorrect value: {}".format(obj.f1))
        self.assertEqual( len(obj.f2), obj.f1, "incorrect length: {} expecting".format(len(obj.f2), obj.f1))

        self.assertEqual( obj.f2[0], 2, "incorrect value: {}".format(obj.f2[0]))
        self.assertEqual( obj.f2[1], 1, "incorrect value: {}".format(obj.f2[1]))
        self.assertEqual( obj.f2[2], 0, "incorrect value: {}".format(obj.f2[2]))

    def test_packing(self):
        data=[0,0,0,3,0,0,0,2,0,0,0,1,0,0,0,0]
        expected_data="".join([chr(x) for x in data])

        packed_result=self.struct.pack(3,[2,1,0])
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 

class EStructComplexEvaluationTestCase(unittest.TestCase):
    def setUp(self):
        self.struct=EStruct('Test','f1 f2.a1 f2.a2','!I{f1}[I{f2[INDEX].a1}[c]]')
             
    def tearDown(self):
        del self.struct
 
    def test_unpacking(self):
        data=[0,0,0,3,
             0,0,0,2,ord('a'),ord('b'),
             0,0,0,1,ord('c'),
             0,0,0,4,ord('d'),ord('o'),ord('g'),ord(' ')]
        data_str="".join([chr(x) for x in data])
                         
        obj=self.struct.unpack(data_str)
        
        self.assertEqual( obj.f1, 3, "incorrect value: {}".format(obj.f1))
        self.assertEqual( len(obj.f2), obj.f1, "incorrect length: {} expecting".format(len(obj.f2), obj.f1))

        self.assertEqual( obj.f2[0].a1, 2, "incorrect value: {}".format(obj.f2[0].a1))
        self.assertEqual( obj.f2[1].a1, 1, "incorrect value: {}".format(obj.f2[1].a1))
        self.assertEqual( obj.f2[2].a1, 4, "incorrect value: {}".format(obj.f2[2].a1))
        
        for v in obj.f2:
            self.assertEqual( len(v.a2), v.a1, "incorrect length: {} expecting".format(len(v.a2), v.a1))

        self.assertEqual( obj.f2[0].a2, ['a','b'], "incorrect value: {}".format(obj.f2[0].a2))
        self.assertEqual( obj.f2[1].a2, ['c'], "incorrect value: {}".format(obj.f2[1].a2))
        self.assertEqual( obj.f2[2].a2, ['d','o','g',' '], "incorrect value: {}".format(obj.f2[2].a2))

    def test_packing(self):
        data=[0,0,0,3,
             0,0,0,2,ord('a'),ord('b'),
             0,0,0,1,ord('c'),
             0,0,0,4,ord('d'),ord('o'),ord('g'),ord(' ')]
        expected_data="".join([chr(x) for x in data])

        packed_result=self.struct.pack(3,[(2,['a','b']),(1,['c']),(4,['d','o','g',' '])])
        self.assertEqual(packed_result,expected_data,"Invalid packing - {}".format(packed_result.encode("hex"))) 
