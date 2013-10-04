from struct import Struct
from collections import namedtuple, OrderedDict

''' Extended the packaging and unpackaging capabilities of Struct module.
Allows for packaging/unpackaging of arrays, conditional packaging/unpackaging, using counts based on other packed fields.
    
Format:
    format= byteorder + format_string
    byte_order= '@'|'='|'<'|'>'|'!'
        @ native byte-order    native size        native alignment
        = native byte-order    standard size      no alignment
        < little endian        standard size      no alignment
        > big endian           standard size      no alignment
        ! network              standard size      no alignment
        
    format_string=      conditonal_format | array_format | normal_format | empty_format
    
    emptry_format=
    
    conditionl_format=  '(' + condition + '?' + true_format + ':' + false_format + ')' 
    condition=          [python evaluation]
    true_format=        format_string
    false_format=       format_string
    An empty format_string implies that no field is required for packinging.
    
    array_format=       count[format_string]
    
    count=              empty_count | constant_count | field_count
    empty_count=
    constant_count=    (0..9)*
    field_count=       '{' + [field_name] + '}'
   
    The [field name] is any field defined prior to this packing element.
    The [python evaluation] is a valid python statement equating to a True or False result. 
    Any field name prior to this packing element may be used. Also for evaulation of array's the index value INDEX may be used
    to specify the current index.
    
Examples:
    !II(f1==1?Q|I)     Network endian, 32 bit integers followed by a 64 but value if f1==1 else another 32 bit integer
    !I{f1}[I{f2[INDEX].a1}[c]]    Network endian, 32 bit integers followed by an array with the number of elements as specified in the field
                                  'f1'. The array elements are a 32 bit integer followed by a number of characters, where that number is set in 
                                  the field 'f2[INDEX].a1', the index is the current iteration of the outer array.
        
'''


class StructObject(object):
    ''' A helper class the help resolve objects within the stucture.
        When packing and unpacking, the data is transformed to or from objects as described by this class.
        The class also creates instances of objects (as a named tuple) from a tuple of data. 
        Partial creation is possible if not enough data for all object fields is available.
        Nesting of objects is also possible.
        
        The __init__ method takes a description string than contains fields and sub fields.
        The string needs to be a space separated list of fields. Nested structures can be created by using a dot notation '.', i.e.
        object.field or object.sub_object.field.
        
        Example:
            'f1 f2 f3.a1 f3.a2 f4 f5.a1.b1 f5.a1.b2 f5.a2.b1 f5.a2.b2'
            This would create the object with fields:
                f1,f2,f3,f4,f5
            f3 is of a type of an object with fields:
                a1, a2
            f5 is of a type of an object with fields:
                a1, a2   with both  fields of an object of type with fields b1 and b2
    ''' 
    
    
    def __init__(self, fields_string, parent=None):
        self.__parent=parent
        self.__fields=self.__parse_fields(fields_string.split())
        
    def __resolve_fields(self, fields):
        return list(OrderedDict.fromkeys([f.split('.')[0] for f in fields]))
      
    def __resolve_sub_fields(self, fields, field):
        return list(OrderedDict.fromkeys([".".join(f.split('.')[1:]) for f in fields if field == f.split('.')[0] and len(f.split('.')[1:]) ])) 
         
    def __parse_fields(self,fields):
        resolved_fields=self.__resolve_fields(fields)
        if len(resolved_fields):
            return OrderedDict([(f, self.__parse_fields(self.__resolve_sub_fields(fields, f))) for f in resolved_fields])
        else:
            return None 
        
    def __fields_str(self, parents=[], fields=None):
        if fields is None:
            return ''
        field_string=''
        for f in fields:
            if fields[f]:
                sub_parents=parents+[f]
                field_string="{}{} ".format(field_string,self.__fields_str(sub_parents,fields[f]))
            else:
                field_string="{}{} ".format(field_string,"{}.{}".format(".".join(parents),f) if parents else f)
                
        return field_string.rstrip()
            
    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.__str__())
    
    def __str__(self):
        return self.__fields_str(fields=self.__fields)
    
    @property
    def Fields(self):
        fields=self.__fields.keys()
        return fields
    
    def SubFields(self, field):
        if field not in self.__fields.keys():
            raise KeyError("Not a field - {}".format(field))
        sub_fields=self.__fields.get(field, None)
        if sub_fields:
            sub_fields=StructObject(self.__fields_str([],sub_fields), self)
        
        return sub_fields
    
    def CreateInstance(self, name, *results):
        fields=self.Fields[:len(results)]
        resolved_results= tuple()
        for f in fields:
            sub_fields=self.SubFields(f)
            if sub_fields and type(results[fields.index(f)]) is not StructObject:
                if type(results[fields.index(f)]) is list:
                    sf_instance=[]
                    for r in results[fields.index(f)]:
                        sf_instance.append(sub_fields.CreateInstance(f,*r))
                    resolved_results = resolved_results +tuple([sf_instance,])                        
                else:
                    sf_instance=sub_fields.CreateInstance(f,*results[fields.index(f)])
                    resolved_results = resolved_results +tuple([sf_instance,])
            else:
                resolved_results = resolved_results+tuple([results[fields.index(f)],])
        return namedtuple(name, self.Fields[:len(results)])._make(resolved_results)
    

class EStruct(object):
    def __init__(self, name, fields_string, format_string):
        self.__name=name
        self.__fields=StructObject(fields_string)

        self.__byteorder='@' if format_string.lstrip()[0] not in ['@','=','<','>','!'] else format_string.lstrip()[0]
        self.__structures=self.__parse_format(format_string.lstrip().lstrip('@=<>!'))
              
    def __parse_format(self,format_string):
        NORMAL_FORMAT=0
        CONDITION=1
        CONDITION_TRUE=2
        CONDITION_FALSE=3
        ARRAY=4
        EVALUATED_COUNT=5
        
        conditional_gaurd_level=0
        array_gaurd_level=0

        state=NORMAL_FORMAT
        
        value=''
        structs=[]
        condition={}
        array={}
        count=''
        evaluated_count=''
        
        for c in format_string:
            if state==NORMAL_FORMAT:
                if c=='(':
                    if len(value):
                        structs.append({"value":value})
                    state=CONDITION
                    condition={}
                    value=''
                elif c=='[':
                    #remove the count if there is one
                    value=value.rstrip(count)
                    if len(value):
                        structs.append({"value":value})
                    state=ARRAY
                    array={}
                    value=''
                elif c=='{':
                    if len(value):
                        structs.append({"value":value})
                    state=EVALUATED_COUNT
                    evaluated_count=''
                    count=''
                    value=''
                else:
                    if c in ['0','1','2','3','4','5','6','7','8','9']:
                        count="{}{}".format(count,c)
                    else:
                        count=''
                    value='{}{}'.format(value,c)
            elif state==EVALUATED_COUNT:
                if c=='}':
                    evaluated_count=value
                    value=''
                    state=NORMAL_FORMAT
                else:
                    value='{}{}'.format(value,c) 
            elif state==ARRAY:
                if c==']' and array_gaurd_level==0:
                    array_values=self.__parse_format(value)
                    array.update({"array":array_values if len(array_values) else [{"value":None}]})
                    if len(evaluated_count):
                        array.update({"eval_count":evaluated_count })
                    else:
                        array.update({"count":0 if len(count)==0 else int(count) })
                    structs.append(array)
                    state=NORMAL_FORMAT
                    value=''
                    count=''
                    evaluated_count=''
                else:
                    if c=='[':
                        array_gaurd_level+=1
                    elif c==']' and conditional_gaurd_level>=0:
                        array_gaurd_level-=1
                    value='{}{}'.format(value,c)
                                   
            elif state==CONDITION:
                if c==')' and conditional_gaurd_level==0:
                    raise Exception("Missing ? in conditional")
                if c=='?' and conditional_gaurd_level==0:
                    condition.update({"eval":value})
                    state=CONDITION_TRUE
                    value=''
                else:
                    if c=='(':
                        conditional_gaurd_level+=1
                    elif c==')' and conditional_gaurd_level>=0:
                        conditional_gaurd_level-=1
                    value='{}{}'.format(value,c)
            elif state==CONDITION_TRUE:
                if c=='|'and conditional_gaurd_level==0:
                    condition_values=self.__parse_format(value)
                    condition.update({"true":condition_values if len(condition_values) else [{"value":None}] })
                    state=CONDITION_FALSE
                    value=''
                else:
                    if c=='(':
                        conditional_gaurd_level+=1
                    elif c==')' and conditional_gaurd_level>=0:
                        conditional_gaurd_level-=1
                    value='{}{}'.format(value,c)
            elif state==CONDITION_FALSE:
                if c==')' and conditional_gaurd_level==0:
                    condition_values=self.__parse_format(value)
                    condition.update({"false":condition_values if len(condition_values) else [{"value":None}] })
                    structs.append(condition)
                    state=NORMAL_FORMAT
                    value=''
                else:
                    if c=='(':
                        conditional_gaurd_level+=1
                    elif c==')' and conditional_gaurd_level>=0:
                        conditional_gaurd_level-=1
                    value='{}{}'.format(value,c) 
        
        if state!=NORMAL_FORMAT:
            raise Exception("untermenated conditional in format")   
        if len(value):
            structs.append({"value":value})
        return structs
    
    def __update_evaluator(self, evaluator, parent, fields, results):
        #need to make a copy of dict
        new_evaluator={k:v for k,v in evaluator.items()}
        if fields is not None and len(fields.Fields[:len(results)]):
            evaluator_object=fields.CreateInstance('_' if parent is None else parent, *results)
            if parent and parent in evaluator:
                #need to make a copy of list
                new_evaluator[parent]=[v for v in new_evaluator[parent]]
                new_evaluator[parent].append(evaluator_object)
            else:
                new_evaluator.update({} if evaluator_object is None else evaluator_object.__dict__)
        return new_evaluator    

    def __unpack_value(self, structure, data, results, evaluator_dict, parent, fields, **kargs):
        struct=None
        value=structure.get("value",None)
        if value is not None:
            struct=Struct(self.__byteorder+value)
        if struct:
            result=struct.unpack_from(data)
            data=data[struct.size:]
        else:
            result=None,
        results=results+result       
        evaluator_dict=self.__update_evaluator(evaluator_dict, parent, fields, results)       
        return results, data, evaluator_dict
    
    def __unpack_array(self, structure, data, results, evaluator_dict, parent, fields, **kargs):
        array=[]
        evaluated_count=structure.get("eval_count",None)
        if evaluated_count is None:
            count=structure.get("count",0)
        else:
            expression=structure["eval_count"]
            expression=expression.replace("[INDEX]","[-1]")
            count=eval(expression,evaluator_dict)   
        
        results=results+(array,)
        
        start_count=count
        while len(data) and (count>0 if start_count else True):
            evaluator_dict=self.__update_evaluator(evaluator_dict, parent, fields, results)
            resolved_name=fields.Fields[len(results)-1]
            sub_fields=fields.SubFields(resolved_name)
            sub_results, data=self.__unpack_results(data,structure["array"],sub_fields,parent=resolved_name,**evaluator_dict)
            if sub_fields is not None and len(sub_fields.Fields):
                results[-1].append(sub_fields.CreateInstance(resolved_name, *sub_results))
            else:
                results[-1].append(sub_results[0])     
            count-=1       

        return results, data, evaluator_dict

    def __unpack_eval(self, structure, data, results, evaluator_dict, parent, fields, **kargs):
        expression=structure["eval"]
        evaluation=eval(expression,evaluator_dict)
        if evaluation and "true" in structure:
            if len(structure["true"]):
                results, data=self.__unpack_results(data,structure["true"],fields,results=results,**evaluator_dict)
        elif not evaluation and "false" in structure:
            if len(structure["false"]):
                results, data=self.__unpack_results(data,structure["false"],fields,results=results,**evaluator_dict)
        return results, data, evaluator_dict

   
    def __unpack_results(self, data, structures, fields,  results=(), parent=None, **kargs):             
        evaluator_dict=kargs
        for s in structures:
            if "value" in s:
                results, data, evaluator_dict=self.__unpack_value(s, data, results, evaluator_dict, parent, fields)
            elif "array" in s:
                results, data, evaluator_dict=self.__unpack_array(s, data, results, evaluator_dict, parent, fields)
            elif "eval" in s:
                results, data, evaluator_dict=self.__unpack_eval(s, data, results, evaluator_dict, parent, fields)

        return results, data
              
    def __find_field(self, structure, evaluator_object):
        count=0
        field_count=0
        for c in structure:
            if c.isdigit():
                count*=10
                count+=int(c)
            elif c in ['s','P']:
                field_count+=1
                count=0
            elif c not in [' ','\t']:
                field_count+=count if count else 1
                count=0
        return getattr(evaluator_object,evaluator_object.__dict__.keys()[field_count])
            
    def __pack_value(self, structure, structure_str, fields_structure_str, evaluator_object, **kargs):
        value=structure.get("value",None)
        if value is not None:
            structure_str='{}{}'.format(structure_str,value)
            fields_structure_str='{}{}'.format(fields_structure_str, value)
        
        return structure_str, fields_structure_str
    
    
    def __pack_array(self, structure, structure_str, fields_structure_str, evaluator_object, **kargs):
        local = kargs
        old_index=kargs.get("INDEX",0)
        
        evaluated_count=structure.get("eval_count",None)
        if evaluated_count is None:
            #structure is constant per index
            if structure.get("count",0):
                count=structure.get("count",0)
            else:
                field=self.__find_field(fields_structure_str, evaluator_object)
                count = len(field)
        else:
            #structure may vary per index
            expression=structure["eval_count"]
            local.update(evaluator_object.__dict__)
            field=self.__find_field(fields_structure_str, evaluator_object)
            expression=expression.replace("[INDEX]","[{}]".format(kargs.get("INDEX",0)) ) #TODO: might need a better default
            count=eval(expression,local)
        if count:
            for i in range(count):
                local.update({"INDEX":i})
                value=self.__pack_structure(structure["array"],evaluator_object, **local)
                structure_str='{}{}'.format(structure_str,value)
        fields_structure_str='{}{}'.format(fields_structure_str,'X')
        
        local.update({"INDEX":old_index})
        return structure_str, fields_structure_str

    def __pack_eval(self, structure, structure_str, fields_structure_str, evaluator_object, **kargs):
        expression=structure["eval"]
        local = kargs
        local.update(evaluator_object.__dict__)
        evaluation=eval(expression,local)
        if evaluation and "true" in structure:
            value=self.__pack_structure(structure["true"],evaluator_object, **kargs)
            structure_str='{}{}'.format(structure_str,value)
            fields_structure_str='{}{}'.format(fields_structure_str,value)
        elif not evaluation and "false" in structure:
            value=self.__pack_structure(structure["false"],evaluator_object, **kargs)
            structure_str='{}{}'.format(structure_str,value)
            fields_structure_str='{}{}'.format(fields_structure_str,value)
        
        return structure_str, fields_structure_str

    def __pack_structure(self, structures, evaluator_object, **kargs):
        #resolve all conditionals
        structure=''
        fields_structure=''
        for s in structures:
            if "value" in s:
                structure, fields_structure = self.__pack_value(s, structure, fields_structure, evaluator_object, **kargs)
            elif "array" in s:
                structure, fields_structure = self.__pack_array(s, structure, fields_structure, evaluator_object, **kargs)
            elif "eval" in s:
                structure, fields_structure = self.__pack_eval(s, structure, fields_structure, evaluator_object, **kargs)
        return structure
    
    def __flatten(self, obj):
        if hasattr(obj, "__dict__"):
            flattend_obj=[]
            for i in obj.__dict__.items():
                if i[1] is not None:
                    result=self.__flatten(i[1])
                    if result is not None:
                        flattend_obj.extend(result)
            return flattend_obj if len(flattend_obj) else None
        elif isinstance(obj, tuple) or isinstance(obj, list):
            flattend_obj=[]
            for i in obj:
                if i is not None:
                    result=self.__flatten(i)
                    if result is not None:
                        flattend_obj.extend(result)
            return flattend_obj if len(flattend_obj) else None            
        else:
            return [obj]
        
    def pack(self, *args, **kargs):
        evaluator_object=self.__fields.CreateInstance(self.__name, *args)
        structure="{}{}".format(self.__byteorder,self.__pack_structure(self.__structures, evaluator_object,**kargs))
        struct=Struct(structure)
        values=self.__flatten(evaluator_object)
        if values:
            values=tuple(values)
            result=struct.pack(*values )
        else:
            result=''
        return result
    
    def unpack(self, data, **kargs):
        results,_ = self.__unpack_results(data,self.__structures,self.__fields,**kargs)                                        
        return self.__fields.CreateInstance(self.__name, *results)
    