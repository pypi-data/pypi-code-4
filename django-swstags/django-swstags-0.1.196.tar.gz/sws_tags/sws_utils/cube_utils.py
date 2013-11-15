import olap.xmla.xmla as xmla
import time
import ujson
import types
from suds import WebFault
import memcache
import re
import random
import math
from django.conf import settings
from sws_tags.sws_utils.messages import *
from django.utils.datastructures import SortedDict



def new_execute(self, command, dimformat="Multidimensional",axisFormat="ClusterFormat", **kwargs):

    """
      **Description:**
            At begin this function  is from xmla library but we have overwrite because the original waste much time.Execute a new mdx against the cube.
      **Args:**
            command : A string which represent the mdx to execute  
      **Returns:**
            A xml file with the result to execute the mdx against the cube
      **Modify:**
            Nothing.
      **Raises:**
            Nothing.
      **Import**::
            Nothing.
      Other information ::
    
    
    """        
    if isinstance(command, types.StringTypes):
        command = {"Statement":command}
    props = {"Format":dimformat, "AxisFormat":axisFormat}
    props.update(kwargs)
    pl = {"PropertyList":props}
    try:
        medio_root =self.client.service.Execute(command, pl)    
        #root=medio_root.ExecuteResponse["return"].root
        #return TupleFormatReader(root)
        return medio_root
    except WebFault, fault:
        swslog('error','Failed method from xmla library',WebFault)
        swslog('error','Failed method from xmla library',fault)
        raise XMLAException(fault.message, listify(fault.fault))

class CUBE:

    """  
            This class is used to connnect with the cube, in that moment the dimensions and measures are calculated
            , and to launch queries against cube.

        **Attributes:**
            #. dimensiones: A dict, the keys are tuples with the name of the dimension first, in second place the attribute of this dimension and in third place 'All' (to explore all values of that attribute) or the attribute again to explore one to one . And the values are the dimension like is needed to create in a mdx .Example: dimensiones={('Client','Client','Client'):'[Client].[Client].[Client]'}
            #. medidas: As the attribute dimension but the keys are different only have two values, the first is 'Measures' for all them , and the second is the measure.Example: medidas={('Measures','Calls'):'[Measures].[Calls]'}
            #. connection: An instance of XMLAProvider after connected with the OLAP services, this attribute is needed to all methods which need the cube parameter.
            #. name: A string , the name of the database where is the cube.
            #. key_memcache: A string which has the key to add and get the dimensiones and medidas attributes in memcache.    
    """

    dimensiones= {}
    medidas={}
    connection=''   #Es del tipo XMLASOURCE
    try:
        name=settings.CUBE_DB_NAME
    except:
        name = 'NO_CUBE_DB_NAME_IN_SETTINGS'
    key_memcache=settings.APP_NAME+'_dimYmed'


    
   
    def connect(self,ip,bbdd=[],cubes=[]):

        """
          **Description:**
                Create connection with OLAP services and get the dimension and medidas from the cubes which are in the databases that we want to connnect.     
          **Args:**
                #. ip: A string with the IP of OLAP service.
                #. bbdd: A list of strings with the names of databases where are the cubes which we will use.
                #. bbdd: A list of strings with the names of cubes which we will use.
          **Returns:**
                An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> : it`s the connection with OLAP service
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
            
        """
        location="http://"+ip+"/OLAP/msmdpump.dll"
        def addDimension_Medidas(ide,value):
     
            if mc.get(ide) == None:
                return mc.set(ide,value,3600)
            return False
        def getDimension_Medidas(ide):
        
            value = mc.get(ide)
            return value[0],value[1]
        def isAdded(ide):
         
            return not (mc.get(ide) == None)
      
    
        mc = memcache.Client([settings.MEMCACHE_IP], debug=0)

        p = xmla.XMLAProvider()
     
        # tiempo=time.time()
        self.connection = p.connect(location=location)
        
        
        
       
        # print not isAdded(self.key_memcache),'!!!!!!!!!!!!!!!!!!!'
        if not isAdded(self.key_memcache):
          
            try:

        
                
                # tiempo=time.time()
                self.medidas=self.__getMedidas(bbdd,cubes) 
                # print '*'*50
                # print 'TIEMPO QUE TARDA EN CALCULAR MEDIDAS = {0}'.format(time.time()-tiempo)
                # print '*'*50
                # print self.medidas,'!!!!!!!!!!!!!!!!!!!'
                
                # tiempo=time.time()
                self.dimensiones=self.__getDimensiones(bbdd,cubes)
                # print '*'*50
                # print 'TIEMPO QUE TARDA EN CALCULAR DIMENSIONES = {0}'.format(time.time()-tiempo)
                # print '*'*50
                # print self.dimensiones,'!!!!!!!!!!!!!!!!!!!'

                value=[]
                value.append(self.medidas)
                value.append(self.dimensiones)
                addDimension_Medidas(self.key_memcache,value)
            except Exception, e:
                swslog('error','wrong location',e)
        else:

            self.medidas,self.dimensiones=getDimension_Medidas(self.key_memcache)

        return self.connection

    def getNamesBBDD (self):

        """
          **Description:**
                Get the names of the databases which are in the ip where we have connected.
          **Args:**
                Nothing.
          **Returns:**
                A lis of strings whit the names of the databases.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
            
        
        """
        row=[]
        try:
      
            
            catalogs=self.connection.getCatalogs()
          
        except Exception, e:
            mc = memcache.Client([settings.MEMCACHE_IP], debug=0)
            mc.delete(self.key_memcache)
            swslog('repeat the connect() whith a good location')
        #colocar de nuevo la option a false si no no deja acceder
        for i in catalogs:
            row.append(i.getUniqueName())
        return row 
    def __getDimensiones(self,bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS'],cubes='NO_CUBE_NAMES_IN_SETTINGS'):

        try: 
            bbdd=[settings.CUBE_DB_NAME]
        except:
            bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS']


        try:
            cubes = settings.CUBE_NAMES
        except:
            cubes = 'NO_CUBE_NAMES_IN_SETTINGS'

        
        dimensiones={}
       
        
        catalogs=self.connection.getCatalogs()
       
        for catalogo in catalogs:
            if catalogo.getUniqueName() in bbdd:
                for Cube in catalogo.getCubes():
                        if Cube.getUniqueName() in cubes:
                            for dim in Cube.getDimensions():
                                for jerar in dim.getHierarchies():
                                    for level in jerar.getLevels():
                                        name=level.getUniqueName()
                                        first_name=name[name.find('[')+1:name.find(']')]
                                        name_aux=name[name.find(']')+1:]
                                        second_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                        name_aux=name_aux[name_aux.find(']')+1:]
                                        third_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                        third_name=third_name.replace('(','').replace(')','')
                                        dimensiones[(first_name,second_name,third_name)]=level.getUniqueName()
        return dimensiones

    def name_dimension(self,axis,complete_name):

        """
          **Description:**
                This method changes the name of dimension from the cubes understand to more readable.
          **Args:**
                #. axis: A list of string which represents a set of dimensions of the cube.
                #. complete_name: A boolean , if it is false return only the name of the dimension , in othre case return the name of the dimension and the attribute , separated by a comma.
          **Returns:**
                A lis of strings whit the names of the dimensions more readable to the human.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
        """
            
        dimensiones =self.dimensiones


        if dimensiones:
            nombres=[]            
            for dimension in axis:
                for dim in dimensiones:
                    if dimensiones[dim]==dimension: 
                       
                        if not complete_name:
                             
                            dim=str(dim[0])
                         
                            position_coma=dim.find(',')
                            
                            nombres.append(dim)
                        else:
                            dim=str(dim[0])+'*'+str(dim[1])
                          
                            position_coma=dim.find(',')
                           
                            nombres.append(dim)



            columnas=sorted(list(set(nombres)))
            return columnas
        else:
            mc = memcache.Client([settings.MEMCACHE_IP], debug=0)
            mc.delete(self.key_memcache)
            return 'cube has not dimensions or it is not good connect'        
    def __getMedidas(self,bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS'],cubes=['Cdrt']):

        try: 
            bbdd=[settings.CUBE_DB_NAME]
        except:
            bbdd=['NO_CUBE_DB_NAME_IN_SETTINGS']


        medidas={}
    
        
        catalogs=self.connection.getCatalogs()
     
        for catalogo in catalogs:

            if catalogo.getUniqueName() in bbdd:

                for Cube in catalogo.getCubes():
                        # print Cube.getUniqueName(),'------------------'
                        if Cube.getUniqueName() in cubes:
                            for medida in Cube.getMeasures():
                               
                                name=medida.getUniqueName()
                                first_name=name[name.find('[')+1:name.find(']')]
                                name_aux=name[name.find(']')+1:]
                                second_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                name_aux=name_aux[name_aux.find(']')+1:]
                                medidas[(first_name,second_name)]=name
        return medidas



    def get_name_BBDD_used(self):

        """
          **Description:**
                This method return the name which we have the cube.
          **Args:**
                Nothing.
          **Returns:**
                A string that is the name of the database which is using.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
        """
    
        return self.name
        

    
    def launch_query(self,mdx=None):

        """
          **Description:**
                This method launch a query against the cube and return the result in xml format.
          **Args:**
                mdx: A string which represents the mdx to launch against the cube
          **Returns:**
                A xml object which has the result to make the query 
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
           
        """
       
        connexion=self.connection
        connexion.client.set_options(retxml=True) 
        connexion.new = new_execute

       
        # tiempoConexion=time.time()
        result = connexion.new(connexion,mdx,Catalog=self.name)
        # print '*'*50
        # print 'TIEMPO QUE TARDA EN LAUNCH QUERY = {0}'.format(time.time()-tiempoConexion)
        # print '*'*50
       

        
        connexion.client.set_options(retxml=False)
        return result

class xml_result:
    """  
            This class is used to get the values from the xml which got from launch a mdx against the cube.

        **Attributes:**
            Nothing.
    """
   
    # Esta clase nos devuelve todos los valores resultantes pasandole el xml que se obtiene al realizar la consulta es solo de uso privado

    def getValues(self,xml1,format_cube=False):

        """
          **Description:**
                This method is to get the values from xml which is the result from launch a mdx against the cube.
          **Args:**
                xml1: A xml which represents the result to launch a mdx against the cube
          **Returns:**
                #. A tuple with 8 elements:
                        #. axis_x_names: A list of strings which have the names of the measures used.
                        #. axis_y_names: A list of strings which have the names of the dimensions used.
                        #. axis_x_values: A list of strings which have the values of the measures used.
                        #. axis_y_values: A list of strings which have the names of the dimensions used.
                        #. numero_filas: An integer which represents the number of rows returns from the cube.
                        #. numero_dimensiones:  An integer which represents the number of dimensions used.
                        #. numero_celdas: A integer which represents the numbers of values returns of all measures.
                        #. numero_medidas: An integer which represents the number of measures used.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        """
       
        NS = '{urn:schemas-microsoft-com:xml-analysis:mddataset}'
        import cElementTree
        
        if xml1.find('ErrorCode')>0:
            # swslog('info','No data','') 
            axis_x_names=''
            axis_y_names=''
            axis_x_values=[]
            axis_y_values=[]
            numero_filas=0
            numero_dimensiones=0
            numero_celdas=0
            numero_medidas=0
            return axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas  
        
        else:

            xml = cElementTree.fromstring(xml1)
            try:
                axes = xml.findall('.//{0}Axes'.format(NS))[0]
            except Exception, e:
                swslog('error','findall',e) 

                error = xml1[xml1.find('<faultstring>')+13:xml1.find('</faultstring>')]
                axis_x_names=''
                axis_y_names=''
                axis_x_values=[]
                axis_y_values=[]
                numero_filas=0
                numero_dimensiones=0
                numero_celdas=0
                numero_medidas=0
                return axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas  
            # print axes.getchildren()[0]
            axis_y= axes.getchildren()[1]


            numero_filas = len(axis_y.getchildren()[0].getchildren())

            if numero_filas == 0:
                axis_x_names=''
                axis_y_names=''
                axis_x_values=[]
                axis_y_values=[]
                numero_filas=0
                numero_dimensiones=0
                numero_celdas=0
                numero_medidas=0
                return axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas  
            numero_dimensiones = len(axis_y.getchildren()[0].getchildren()[0].getchildren())

            
            axis_y_names = [axis_y.findall('.//{0}Member'.format(NS))[i].findall('.//{0}LName'.format(NS))[0].text for i in range(0,numero_dimensiones) ]
            # print 'axis_y_names   ',axis_y_names
            axis_y_values = [i.text for i in axis_y.findall('.//{0}Caption'.format(NS))]
            # print 'axis_y_values   ',axis_y_values
           
            axis_x= axes.getchildren()[0]
            # print 'axis_x',axis_x
            axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]
            # print 'axis_x_names',axis_x_names
            numero_medidas = len(axis_x_names)
            # print 'numero_medidas',numero_medidas

            if format_cube:
                
                axis_x_values = xml.findall('.//{0}CellData//{0}FmtValue'.format(NS))
                axis_x_values = [i.text.encode('ascii','ignore') for i in axis_x_values]
                
                
            else:
                axis_x_values = xml.findall('.//{0}CellData//{0}Value'.format(NS))
                axis_x_values = [i.text for i in axis_x_values]
                
                    

            

                
           
            
            numero_celdas=len(axis_x_values)
        
            return (axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas)

class Salida_Highcharts:
    """  
            This class is used to get  a string format in json for a HighChart.

        **Attributes:**
            Nothing.
    """
    

    def result_to_json(self,cube,result,types={},xAxis=['Time','Date'],dimension_v_name='client',exclude=[],request_data={},complete_name=False,format_cube=False):
        
        """
          **Description:**
                This method is to convert the values get from xml to a dict for a highchart. 
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. types: A list with types to draw each dimension in the highchart -->  types=['spline','column']
                #. xAxis: A list with the names of the dimension which will appear en the x axis.
                #. dimension_v_name: A string with the value of the dimension which appear in the y axis.
                #. exclude: A dict with the names o f values to exclude and theirs values.
                #. complete_name: A boolean which indicate if the names of the dimension will be the dimension and the attribute (true) or only the dimension.

          **Returns:**
                A dict with the elements need to form a HighChart.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
        
        """
        
            
        import time
        t0 = time.time()
        
        t1 = time.time()
        
        xml_class=xml_result()

       
      
        types2={}
        for i in types:
            types2[i.upper()]=types[i]

        types=types2

        c={}
        for i in exclude:
            c[i.keys()[0]]=0

        axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = xml_class.getValues(result,format_cube)
        axis_y_names = cube.name_dimension(axis_y_names,complete_name)

        
        value_type=[]
        for i in range(0, len(axis_y_values)):
            value =  axis_y_values[i]
            name = axis_y_names[int(math.fmod(i,len(axis_y_names)))]
            if name == 'Date' and  len(value) ==1:
                value = '0'+value
            
            value_type.append((name,value))

        new_date = []

        dim = ''
        for d in axis_y_names:
            if d != 'Time' and d != 'Date':
                dim = d

        if len(axis_y_names) == 3:
            for i in range(0,len(value_type)):
                
                if value_type[i][0] == 'Date':
                    part_Date = value_type[i][1]
                    part_Date = part_Date[0:4]+'-'+part_Date[4:6]+'-'+part_Date[6:8]

                    try: 
                        if value_type[i+1][0] == 'Time':
                            part_Time = value_type[i+1][1]
                        elif value_type[i+2][0] == 'Time':
                            part_Time = value_type[i+2][1]
                    except Exception, e:
                        part_Time = '00:00'
                        swslog('error','index out of range',e)
                        
                    
                    date = part_Date +' '+ part_Time
                    new_date.append(date)
                elif value_type[i][0] ==dim:
                    new_date.append(value_type[i][1])

            axis_y_values = new_date

            axis_y_names.remove('Time')
            numero_dimensiones = 2

        elif len(axis_y_names) == 2:
            for i in range(0,len(value_type)):
                if value_type[i][0] == 'Date':  
                    part_Date = value_type[i][1]
                    part_Date = part_Date[0:4]+'-'+part_Date[4:6]+'-'+part_Date[6:8]
                    new_date.append(part_Date) 

                elif value_type[i][0] ==dim:
                    new_date.append(value_type[i][1])
            axis_y_values = new_date


        if c:
            for i in c.keys():
                axis_y_names.remove(i[0])
            position=0
            for i in range(0,len(axis_y_names)):

                if axis_y_names[i]==c.keys()[0][0]:
                    position=i
            part_Dates_y=[]
            for i in range(0,len(axis_y_values)):
                if i%numero_dimensiones != position:
                    part_Dates_y.append(axis_y_values[i])                


            axis_y_values=part_Dates_y
            numero_dimensiones=numero_dimensiones - len(c.keys())

        
        position_dimension_v_name=0

        for i in range(0,len(axis_y_names)):
            if axis_y_names[i] == xAxis[0] :
                position_dimension_v_name=i
                xAxis=xAxis[0]
            elif axis_y_names[i] == xAxis[1]:
                position_dimension_v_name=i
                xAxis=xAxis[1]
        ##GENERALIZAR 
        todo={}


        v_xAxis=[axis_y_values[i*numero_dimensiones+position_dimension_v_name] for i in range(0,len(axis_y_values)/2)]
      
        v_xAxis=sorted(list(set(v_xAxis)))
                   
        
        for j in range(0,numero_dimensiones):

            todo[axis_y_names[j]]=[axis_y_values[i*numero_dimensiones+j] for i in range(0,len(axis_y_values)/numero_dimensiones)]
            todo[axis_y_names[j]]=sorted(list(set(todo[axis_y_names[j]])))

        if todo:
            new_xAxis = []
            for r in todo[xAxis]:
                if len(r)==1:
                    r = '0'+r
                new_xAxis.append(r)



            v_xAxis=new_xAxis

            v_xAxis=sorted(new_xAxis)

            value_xAxis=todo[dimension_v_name]
           

            
            v_name=[]
            
            for i in axis_x_names:
                for j in value_xAxis:
                    v_name.append(str(j)+i.upper())
            
            v_name= sorted(list(set(v_name)))
            v_type=[]
            v_yAxis=[]
           
            cont = 0
            for i in v_name:
                for j in types:  
                    
                    if j in i:
                        v_type.append(types[j])
                        v_yAxis.append(cont)
                        if cont == 0:
                            cont = 1
                        else:
                            cont = 0
           

            index1=0
            index2=numero_filas
            rows=[]
            for fila in range(index1,index2):
                    row={}
                    for i in axis_y_names:
                        row[i]=''
                    for i in axis_x_names:
                        row[i.lower().replace(' ','_')]=''

                    for measure in range(0,numero_medidas):
                        row[axis_x_names[measure].lower().replace(' ','_')] = str(axis_x_values[(fila*numero_medidas)+measure])
                        
                    for dimension in range(0,numero_dimensiones):

                        if isinstance(axis_y_values[(fila*numero_dimensiones)+dimension],unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)
            v_data={}
            for i in v_name:
                v_data[i]=[]

            for row in rows:
                if row[dimension_v_name] in  str(v_name):
                    for i in axis_x_names:
                        a = i # this is a patch for the problem of a measure with two or more word
                        i = i.replace(' ','_')
                        if format_cube:
                            row[i.lower()] = row[i.lower()].replace(',','')
                            row[i.lower()] = row[i.lower()].replace('%','')
                            a = i.replace('_',' ')
                        v_data[str(row[dimension_v_name])+a.upper()].append(float(row[i.lower()]))
            ## Para rellenar cada fila hasta el maximo 
            v_data2=[]
            mayor=0
           
            for i in  sorted(list(set(v_data.keys()))):
                if len(v_data[i])>mayor:
                    mayor=len(v_data[i])
                v_data2.append(v_data[i])

            for i in v_data2:
                while len(i)<mayor:
                    i.append(0)
            v_data= v_data2


            # TODOMAS BUG CAIDA EMPICADA DE LA GRAFICA EN LA ULTIMA REPRESENTACION 
            # a=v_yAxis.pop()
            # b=v_xAxis.pop()

            dict_higcharts={}
            dict_higcharts['v_data']=v_data
            dict_higcharts['v_name']=v_name
            dict_higcharts['v_type']=v_type
            dict_higcharts['v_yAxis']=v_yAxis
            dict_higcharts['v_xAxis']=v_xAxis


            
            return dict_higcharts
        else:
            dict_higcharts={}
            dict_higcharts['v_data']=[]
            dict_higcharts['v_name']=[]
            dict_higcharts['v_type']=[]
            dict_higcharts['v_yAxis']=[]
            dict_higcharts['v_xAxis']=[]
            return dict_higcharts
      


class Salida_Grid:
    """          
            This class is used to get the filter and a string format in json for a grid

        **Attributes:**
            Nothing.
   
    """
    
        
    # Formatea los resultados obtenidos ejecutar una mdx en el paso anterior a json
    def result_to_json(self,cube,result,database_cube_dict=[],isfilter=False,rowNum=500,page=0,total=False,complete_name=False,format_cube=False):

        """
          **Description:**
                This method correspond with all views whre there are grids which use data from the cube. This function convert the values get from xml (result to launch a mdx ) to a string in json format for a grid. 
          **Args:**
                #. cube: The cube object which has been used to launch the mdx.
                #. result: A xml object get to launch the mdx.
                #. database_cube_dict : A dict with the names of dimension return from the cube like keys and the values with the names that we ant that appear in json string.
                #. isfilter : A boolean which indicate if the result ton convert in json is for a filter or not.
                #. rowNum : A integer which indicate the number of rows that we want in the json.
                #. page : A integer which indicate the number of page that we want in the json. If the rowNum is 200 and the page is 2 ,we will get from 200 row to 400 row. If the page is 0 we will get all the rows.
                #. total : A boolean. If it is true, the json will contain the total of all measures.
                #. complete_name: A boolean which indicate how we want the name of the dimension, if it is true the name will be : name of the dimension * attribute , in other case only the name of the dimension.
          **Returns:**
                A string in json format.
          **Modify:**
                Non modify anything.
          **Raises:**
                IndexError: The errors and warnning of the views are storage in the archive ...
          **Import**::
                Nothing.
          Other information ::
        
        
        """
        
             
    
        xml_class=xml_result()

        #axis_x,axis_x_names,axis_y,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = self.__getValues(xml)
        axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = xml_class.getValues(result,format_cube)

        if numero_celdas==0:
            axis_x_names=''
            axis_y_names=''
            axis_x_values=[]
            axis_y_values=[]
            numero_filas=0
            numero_dimensiones=0
            numero_celdas=0
            numero_medidas=0
            
        i=0
        for name in axis_x_names:
            if name == 'ACD':
                index_name = i
            i = i+1

        ##axis_x_names al hacer el json salen duplicados y uno de ellos vacio 
        ##axis_ynames al hacer el json deberia de salir el nombre mejor 
       
      
        axis_y_names = cube.name_dimension(axis_y_names,complete_name)
        
        if isfilter:
            list_dict = []
            list_dict.append({'text':'----','id':'NULL'})
            if numero_dimensiones==2:
                for i in range(0,len(axis_y_values)/2):

                    list_dict.append({'id': str(axis_y_values[(i*2)+1]),'text':axis_y_values[i*2]})

                return list_dict
            else:
                for i in range(0,len(axis_y_values)):

                    list_dict.append({'id': str(axis_y_values[(i)]),'text':axis_y_values[i]})

                return list_dict
        else:
           
            data = {}
            rows = []

            if page==0:
                data['total']=numero_filas
            else:
                numero_filas=numero_filas+0.0
                total = numero_filas / rowNum
                if total.is_integer():
                    data['total'] = total
                else:
                    if int(str(total)[str(total).find('.')+1])>5:
                        data['total']=int(str(total)[str(total).find('.')-1])+1
                    else:
                        data['total']=int(str(total)[str(total).find('.')-1])

            numero_filas = int(numero_filas)
            data['records'] = numero_filas

            if page==0:
                index1=0
                index2=numero_filas
            else:
                page = int(page)
                index1 = int((page-1) * rowNum)
                index2 = int(page*rowNum)
                if numero_filas<index2:
                    index2 = numero_filas
            if total:
                totales={}
                for i in axis_x_names:
                    # totales[i.replace(' ','_')]=0
                    totales[i]=0
              
            cont_ACD_NAN=0
            for fila in range(0,numero_filas):

                # row={}

                row = SortedDict()

                for i in axis_y_names:
                    row[i]=''
                for i in axis_x_names:
                    # row[i.replace(' ','_')]=''
                    row[i]=''


                # print row



                for measure in range(0,numero_medidas):
                    # row[axis_x_names[measure].replace(' ','_')] = str(axis_x_values[(fila*numero_medidas)+measure])

                    # print 'aaa->',axis_x_values[(fila*numero_medidas)+measure]

                    if fila < index2 and fila >= index1:                                                
                        if axis_x_values[(fila*numero_medidas)+measure]!='NaN':
                            if format_cube:
                                row[axis_x_names[measure]] = str(axis_x_values[(fila*numero_medidas)+measure])
                            else:
                                row[axis_x_names[measure]] = str(round(float(axis_x_values[(fila*numero_medidas)+measure]),4))
                        else:
                            row[axis_x_names[measure]] = '0'

                    # print row

                    if total:
                            if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                                if not format_cube:
                                    totales[axis_x_names[measure]]+=round(float(axis_x_values[(fila*numero_medidas)+measure]),4)
                            else:
                                if measure == index_name: # index for measure ASR 
                                    cont_ACD_NAN = cont_ACD_NAN +1
                      
                if fila < index2 and fila >= index1:

                    for dimension in range(0,numero_dimensiones):
                        if database_cube_dict:
                            for key,value in database_cube_dict.items():
                                if axis_y_names[dimension] == key:
                                    axis_y_names[dimension] = value


                        #### TODO_MAS EL KEY DE DATABASA_CUBE DICT VIENE CON UNA COMA AL PRINCIPIO
                        axis_y_names[dimension]=axis_y_names[dimension].lstrip("'")
                        if isinstance(axis_y_values[(fila*numero_dimensiones)+dimension],unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)
            
           
            if total:
                if not format_cube:
                    total_cost = 0
                    total_income=0

                    json_data_new={}
                    for k,v in totales.items():
                        sign = 1
                        if float(v)<0:
                            sign = -1
                        v=str(v)

                        p = re.compile('\d+')
                        c= p.findall(v)

                        # print 'ccc->',c
                        if len(c)>1:
                            v= str(c[0])+'.'+str(c[1])[0:2]
                            v = str(float(v)*sign)
                        
                        if (k.find('Avg')>0) or (k == 'ASR') or (k=='ACD'):
                            try:
                                if (k!='ACD'):
                                    v = str(float(v)/len(rows))
                                else:
                                    div = len(rows)-cont_ACD_NAN
                                    v = str(float(v)/div)

                                v = v[0:6] 

                            except Exception, e:
                                swslog('error','div for 0',e)

                        if k == 'Total Income':
                            total_income = v
                        if k == 'Total Cost':
                            total_cost = v

                        json_data_new[k]=v

                        total_cost = float(total_cost)
                        if total_cost != 0: # sino dejo el sumatorio 
                            benefic = float(total_income) - float(total_cost)  
                            json_data_new['Margin'] =float(benefic) / float(total_cost) * 100
                        data['footerData']=json_data_new

            data['rows']=rows
            data['page'] = page
            obj=json.dumps(data)
    #############################
            return obj
    

    # Pasando una query obtenemos los filtros necesarios para esta, uno a uno 
    def filters(self,query,cube,database_cube_dict,dimensiones=[],exclude_rows=[],dimension_extra='Id'):

        """
          **Description:**
                This function is used to get all the filters acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used 
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. dimensiones: A list of dimensions which calculate the mdx to get the filters if it is not used the filters will be calculated according to all dimensions.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """

       
        if not dimensiones:
            dimensiones= cube.dimensiones
       

        cmd=''
        row=''
        p=0

        for dim in dimensiones:
                row=self.filter(query,cube,dim,database_cube_dict,exclude_rows,dimension_extra)
        return row
        
    def filter(self,query,cube,dimension,database_cube_dict=[],exclude_rows=[],dimension_extra='Id'):
        """
          **Description:**
                This function is used to get one filter acording to the mdx which we have used.
          **Args:**
                #. query: A string which is a mdx
                #. cube: The cube object which has been used 
                #. dimensiones: A string with the dimension which calculate the mdx to get the filter.
                #. database_cube_dict: A dict with the names of the dimension which the cube returns and the names that we want.
                #. exclude_rows: A dict with the name of a dimension and like value that we want to exclude from the filters.
          **Returns:**
                A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
          **Modify:**
                Non modify anything
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::

        """
 
        mdx_class=MDX()
        query_without_select,measure=mdx_class.without_select(query)
        
        
        json=''
        on_rows=[]
        # print 'empezamooooooooooos'
        on_rows.append(dimension)
        if dimension_extra!='None':
            dimension_id=(dimension[0],dimension_extra,dimension_extra)
            on_rows.append(dimension_id)
        select=mdx_class.select_for_filter(cube,on_rows=on_rows,medida=measure,exclude_rows=exclude_rows)
        query =select + query_without_select
        # print 'MDX FILTERS  -->  ',query
        res=cube.launch_query(mdx=query.upper())

        json=self.result_to_json(cube,res,database_cube_dict,isfilter=True)
        return json
class MDX:

    """          
            This class is used to create mdx to launch against the cube.
        **Attributes:**
            Nothing.
   
    """

    # Esta funcion decuelve la misma query que se le pasa como parametro pero sin la parte select de la misma
    def without_select(self,query):

        """
          **Description:**
                This function is used to return the same mdx that we pass but without select part, then it will be modify.
          **Args:**
                query: A string which has the mdx.
          **Returns:**
                This function  return a string which is the same mdx that we pass but without select part
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
        
        """
        
            

        query=query.lower()
        inicio=query.find('rows')+4
        medida=query[inicio:]
        inicio=medida.find('[')
        medida=medida[inicio:]
        final = medida.find('.')
        medida_aux=medida[final:]
        final+=medida_aux.find(']')
        medida=medida[:final+1]
        position_rows=query.find('from')
        query=query[position_rows:]
        return query,medida

    def without_rows(self,query):

        """
          **Description:**
                This function is used to return the same mdx that we pass but without select part, then it will be modify.
          **Args:**
                query: A string which has the mdx.
          **Returns:**
                This function  return a string which is the same mdx that we pass but without select part
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information ::
        
        
        """
        
            

        query=query.lower()
        inicio=query.find('rows')
        rows=query[inicio:]


        coma=rows.find(',')+1
        query=rows[coma:]
        return query

    

    def __non_empty(self,part_NON_EMPTY):
        if part_NON_EMPTY:
            return ' non empty '
        else:
            return' '

    def __rows_or_columns(self,cube,rows,part=[],range_rows={},exclude_rows={},part_order={},part_filter={}):
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        order=''
        med_concrete=''
        dim_concrete=''
        for i in part_order:
            if i in dimensiones:
                order='dim'
                dim_concrete=i
            elif i in medidas:
                order='med'
                med_concrete=i
            else:
                order='null'
        mdx=''
        new_part=[]
      

        if part_order and order=='dim':
            part.remove(part_order.keys()[0])
            part.insert(0,part_order.keys()[0])
        if part_order and order!='null':
            if  part_order[part_order.keys()[0]]=='ASC'  or part_order[part_order.keys()[0]]=='BASC' :
                mdx+='bottomcount('
            else:
                mdx+='topcount('
        if part:
            if rows:
                mdx+=' ('
            else:
                mdx+=' {' 
            for on_row in part:
                if on_row in dimensiones:
                    
                    filtrar_dim=on_row in part_filter
                    if filtrar_dim:
                            mdx+='filter('

                    if on_row in range_rows:                      
                        position=dimensiones[on_row].find('.')+1
                        dim=dimensiones[on_row][position:]
                        position+=dim.find('.')+1
                        mdx+=dimensiones[on_row][:position]+'&['+range_rows[on_row][0]+']:'
                        mdx+=dimensiones[on_row][:position]+'&['+range_rows[on_row][1]+']'
                        if on_row in exclude_rows:
                            for dim in exclude_rows[on_row]:

                                mdx+='-'+dimensiones[on_row][:position]+'&['+dim+']'
                    else:
                        position=dimensiones[on_row].find('.')+1
                        dim=dimensiones[on_row][position:]
                        position+=dim.find('.')+1
                        mdx+= dimensiones[on_row]
                        for exclude in exclude_rows:
                            if on_row in exclude: 
                                mdx+='-'+dimensiones[on_row][:position]+'&['+ exclude[on_row]+']'
                    if filtrar_dim:
                        position=dimensiones[on_row].find('.')+1
                        dim=dimensiones[on_row][position:]
                        position+=dim.find('.')+1
                        if len(part_filter)>1:
                            signo=part_filter[on_row][0]
                            value=part_filter[on_row][1]
                            mdx+= ','+dimensiones[on_row][:position]+'CurrentMember.Name'+signo+'"'+value+'")'
                        else:
                            value=part_filter[on_row][1]
                            mdx+= ','+dimensiones[on_row][:position]+'CurrentMember.Name="'+value+'")'
                    mdx+=','
                    
                elif on_row in medidas:
                    mdx+= medidas[on_row]+','
                else:
                    swslog('error','Failed MDX class','<<error in {0} >>'.format(str(on_row)))
                    mdx+='<<error in {0} >>'.format(str(on_row))

            mdx=mdx[0:len(mdx)-1]
            if rows:    
                mdx+=') '
            else:
                mdx+='} ' 
            if part_order and order=='dim':
                mdx+= ',100000000)'
            elif part_order and order=='med':
                medida=part_order.keys()[0]
                medida_mdx='['+medida[0]+']'+'.['+medida[1]+']'
                mdx+=',100000000,'+medida_mdx+')'

                
        return mdx
  

    def partDate(self,part_where,fecha,cube):

        """
          **Description:**
                This function is used to create the part where when we use date and time dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. fecha:  A string which contain the date that we used.
                #. cube: The cube object which has been used  
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :
        
        """
        # print '___________',part_where
        # print '___________',fecha
        
            
        mdx=''
        dimensiones=cube.dimensiones
        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(fecha)+'] ) *'
        for i in part_where:
          
            if 'Time' in i:
                if i in dimensiones:

                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(part_where[i][0])+'] : '+w[:position_value]+'&['+str(part_where[i][1])+']) *'
    
        for i in part_where:
          
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                   
            elif 'Time' in i:
                if i in dimensiones:

                    dimension=dimensiones[i]        
   
            else:
                 
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    # print w[:position_value]
                    if type(part_where[i])is str or type(part_where[i])is unicode:
                        mdx+='('+w[:position_value]+'&['+str(part_where[i])+'] ) *'
                    elif (type(part_where[i]) is tuple):
                        if part_where[i][0] == '-' and type(part_where[i][1]) ==str: # case filter exclude

                            exclude = str(part_where[i][0])+w[:position_value]+'&['+part_where[i][1]+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'
                        
                        elif part_where[i][0] == '-' and type(part_where[i][1]) == list:
                            exclude = ''
                            for n in part_where[i][1]:
                                exclude = exclude + str(part_where[i][0])+w[:position_value]+'&['+n+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'

                        elif part_where[i][0] == '' and type(part_where[i][1]) == list:
                            # TODOMAS need to include a list of case positive
                            exclude = ''
                            for n in part_where[i][1]:
                               
                                exclude = exclude + '-'+w[:position_value]+'&['+n+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'
                    
                  

        #TODO MAS 

        mdx= mdx[:-1]
        return mdx

    def partComplete(self,part_where,cube,nuevas_fechas):
        """
          **Description:**
                This function is used to create the part where when we use data dimension.
          **Args:**
                #. part_where: A list that contain al the data need to create the where
                #. nuevas_fechas:  A list of string which contain the dates that we used.
                #. cube: The cube object which has been used  
          **Returns:**
                Part of the where of a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
                Nothing.
          Other information :
        
        """
        # print '........................',part_where
        # print '........................',nuevas_fechas
        mdx=''
        dimensiones=cube.dimensiones
        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+nuevas_fechas[0]+'] : '+w[:position_value]+'&['+nuevas_fechas[1]+']) *'
       
        for i in part_where:
          
            if 'Time' in i:
                if i in dimensiones:

                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&[0] : '+w[:position_value]+'&[2359]) *'
    

        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                   

            elif 'Time' in i:
                if i in dimensiones:
                   dimension=dimensiones[i] 
            else:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                   
                    if type(part_where[i])is str or type(part_where[i])is unicode:
                        mdx+='('+w[:position_value]+'&['+str(part_where[i])+'] ) *'
                    
                    elif type(part_where[i]) is tuple:
                       
                        if part_where[i][0] == '-' and type(part_where[i][1]) ==str: # case filter exclude

                            exclude = str(part_where[i][0])+w[:position_value]+'&['+part_where[i][1]+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'
                        
                        elif part_where[i][0] == '-' and type(part_where[i][1]) == list:
                            exclude = ''
                            for n in part_where[i][1]:
                                exclude = exclude + str(part_where[i][0])+w[:position_value]+'&['+n+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'

                        elif part_where[i][0] == '' and type(part_where[i][1]) == list:
                            # TODOMAS need to include a list of case positive
                            exclude = ''
                            for n in part_where[i][1]:
                               
                                exclude = exclude + '-'+w[:position_value]+'&['+n+'] '
                            mdx+='('+'['+str(i[0])+'].'+'['+str(i[1])+'].'+'['+str(i[2])+']'+ exclude +' )*'


                


        mdx= mdx[:-1]
        return mdx
    def __where_dict2(self,cube,part_where={},request_data={}):  
        # print '----------------------'
        # print 'part_where',part_where
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        dimension_members=''
        tiempo={'Time':False,'Date':False}
        for i in part_where:
            if i[0]in tiempo:
                tiempo[i[0]]=i
                dim_time=i
        nuevas_fechas=(part_where[dim_time][0][:-6],part_where[dim_time][1][:-6])
        # print 'EMPEZAMOS'*5
        # print part_where
        # if not 'int_all_time' in request_data:
        #     request_data['int_all_time']=0
        # if not request_data['int_all_time']:
        if part_where:
            ## PARA VER QUE CASO DEL WHERE ES
            
            if tiempo['Date']:
                fecha_comienzo=int(part_where[dim_time][0][8:-2])==0
                fecha_fin=int(part_where[dim_time][1][8:-2])==2359

            #### SI LAS FECHAS SON COMPLETAS
            if fecha_comienzo and fecha_fin:
                # print 'FECHAS COMPLETAS'
                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'

            ###### Si las fechas no son completas por el final 
            elif fecha_comienzo:
                # print 'FECHAS IMCOMPLETAS POR EL FINAL'
                nuevas_horas=(0,int(part_where[dim_time][1][8:-2]))
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                #no son completas por el final
                

                mdx+='{'+self.partDate(part_where,nuevas_fechas[1],cube)+'} +'
                # Habria que restar 1 a la fecha en formato fecha puesto que de este modo pueden salir fechas erroneas , pero aun asi la mdx funciona correctamente.
                nueva=int(nuevas_fechas[1])-1
                nuevas_fechas=(nuevas_fechas[0],str(nueva))

                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'


            ###### Si las fechas no son completas por el principio 
            elif fecha_fin:
                # print 'FECHAS IMCOMPLETAS POR EL PRINCIPIO'
                nuevas_horas=(int(part_where[dim_time][0][8:-2]),2359)
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                
                mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'


                nueva=int(nuevas_fechas[0])+1
                nuevas_fechas=(str(nueva),nuevas_fechas[1])
               

                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} '
            ########################
            ###### Si las fechas no son completas por ninguno de los extremos
            else:
                # print 'FECHAS IMCOMPLETAS POR TODOS LOS LADOS'
                
                nuevas_horas=(int(part_where[dim_time][0][8:-2]),int(part_where[dim_time][1][8:-2]))
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                
                if int(nuevas_fechas[1])-int(nuevas_fechas[0])==1:
                    # print 'un dia'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(0,part_where[i][1])
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]
                    
                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(part_where[i][0],2359)
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]

                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[0],cube)+'} +'
                elif int(nuevas_fechas[1])-int(nuevas_fechas[0])==0:
                    # print nuevas_fechas[1],' ',nuevas_fechas[0]
                    # print 'cero dias'
                    # print part_where
                   
                    mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'

                else:
                    # print 'mas de un dia'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(0,part_where[i][1])
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]

                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                    if nuevas_fechas[0]!=nuevas_fechas[1]:
                        part_where_aux={}
                        for i in part_where:
                           
                            if 'Time' in i :
                                aux=(part_where[i][0],2359)
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]
                        mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[0],cube)+'} +'

                        nueva1=int(nuevas_fechas[1])-1
                        nueva0=int(nuevas_fechas[0])+1
                        nuevas_fechas=(str(nueva0),str(nueva1))
                        
                        part_where_aux={}
                        for i in part_where:
                           
                            if 'Time' in i :
                                aux=(part_where[i][0],2359)
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]

                        mdx+='{'+self.partComplete(part_where_aux,cube,nuevas_fechas)+'} '
            mdx=' where ( ' + mdx[:-1] + ' )'  
#         else:
#             nuevas_horas=(int(part_where[dim_time][0][8:-2]),int(part_where[dim_time][1][8:-2]))
#             mdx = ' where ( ' + '{([Time].[Time Field].&[' + str(nuevas_horas[0])+ '] : [Time].[Time Field].&['+str(nuevas_horas[1])+']) *([Date].[Id].&['+str(nuevas_fechas[0])+'] : [Date].[Id].&['+str(nuevas_fechas[1])+'])} *'
#             for i in part_where:
#                 if 'Date' in i:
#                     dimension=dimensiones[i]        

#                 elif 'Time' in i:
#                     dimension=dimensiones[i]        
 

#                 else: 
# ### case where 

#                     if i in dimensiones:
                       
#                         dimension=dimensiones[i]        
#                         join=''
#                         w= dimension
#                         position_value=w.find('.')+1
#                         w2=w[position_value:]
#                         position_value+=w2.find('.')+1


#                         mdx+='{('+w[:position_value]+'&['+str(part_where[i])+'] )} *'

#             mdx= mdx[:-1] + ')'

        return mdx





    def __where_dict(self,cube,part_where={},request_data={}):  
      
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        dimension_members=''
        tiempo={'Time':False,'Date':False}
        for i in part_where:
            if i[0]in tiempo:
                tiempo[i[0]]=i
                dim_time=i
        nuevas_fechas=(part_where[dim_time][0][:-6],part_where[dim_time][1][:-6])
        numero_dias=int(nuevas_fechas[1])-int(nuevas_fechas[0])
        
        if part_where:
            ## PARA VER QUE CASO DEL WHERE ES
            
            if tiempo['Date']:
                fecha_comienzo=int(part_where[dim_time][0][8:-2])==0
                fecha_fin=int(part_where[dim_time][1][8:-2])==2359

            #### SI LAS FECHAS SON COMPLETAS
            if ((fecha_comienzo and fecha_fin)and numero_dias>=1):
                # print 'FECHAS COMPLETAS'
                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'

            ###### Si las fechas no son completas por el final 
            elif (fecha_comienzo and numero_dias>=1):
                # print 'FECHAS IMCOMPLETAS POR EL FINAL'
                nuevas_horas=(0,int(part_where[dim_time][1][8:-2]))
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                #no son completas por el final
                

                mdx+='{'+self.partDate(part_where,nuevas_fechas[1],cube)+'} +'
                # Habria que restar 1 a la fecha en formato fecha puesto que de este modo pueden salir fechas erroneas , pero aun asi la mdx funciona correctamente.
                nueva=int(nuevas_fechas[1])-1
                nuevas_fechas=(nuevas_fechas[0],str(nueva))

                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'


            ###### Si las fechas no son completas por el principio 
            elif (fecha_fin and numero_dias>=1):
                # print 'FECHAS IMCOMPLETAS POR EL PRINCIPIO'
                nuevas_horas=(int(part_where[dim_time][0][8:-2]),2359)
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                
                mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'


                nueva=int(nuevas_fechas[0])+1
                nuevas_fechas=(str(nueva),nuevas_fechas[1])
               

                mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} '
            ########################
            ###### Si las fechas no son completas por ninguno de los extremos
            else:
                # print 'FECHAS IMCOMPLETAS POR TODOS LOS LADOS'
                
                nuevas_horas=(int(part_where[dim_time][0][8:-2]),int(part_where[dim_time][1][8:-2]))
                part_where[('Time','Time Field','Time Field')]=nuevas_horas
                
                if int(nuevas_fechas[1])-int(nuevas_fechas[0])==1:
                    # print 'un dia'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(0,part_where[i][1])
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]
                    
                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(part_where[i][0],2359)
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]

                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[0],cube)+'} +'
                elif int(nuevas_fechas[1])-int(nuevas_fechas[0])==0:
                    # print nuevas_fechas[1],' ',nuevas_fechas[0]
                    # print 'cero dias'
                    # print part_where
                   
                    mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'

                else:
                    # print 'mas de un dia'
                    part_where_aux={}
                    for i in part_where:
                        
                        if 'Time' in i :
                            aux=(0,part_where[i][1])
                            part_where_aux[i]=aux
                        else:
                            part_where_aux[i]=part_where[i]

                    mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                    if nuevas_fechas[0]!=nuevas_fechas[1]:
                        part_where_aux={}
                        for i in part_where:
                           
                            if 'Time' in i :
                                aux=(part_where[i][0],2359)
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]
                        mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[0],cube)+'} +'

                        nueva1=int(nuevas_fechas[1])-1
                        nueva0=int(nuevas_fechas[0])+1
                        nuevas_fechas=(str(nueva0),str(nueva1))
                        
                        part_where_aux={}
                        for i in part_where:
                           
                            if 'Time' in i :
                                aux=(part_where[i][0],2359)
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]

                        mdx+='{'+self.partComplete(part_where_aux,cube,nuevas_fechas)+'} '
            mdx=' select ( ' + mdx[:-1] + ' ) on columns from'  


        return mdx




  

    def __order(self,cube,order,part_order):
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=', '
        if order in dimensiones:
            dimension = dimensiones[order]
            p_pto=dimension.find('.')+1
            d=dimension[p_pto:]
            p_pto+=d.find('.')
            dimension=dimension[0:p_pto+1]+'membervalue'

            mdx+= dimension+', '+part_order[order]

        elif order in medidas:
            mdx+= medidas[order]+', '+part_order[order]
        else:
            swslog('error','Failed MDX class','<<error in order {0}>> '.format(str(order)))
            mdx+='<<error in order {0}>> '.format(str(order))
        mdx+=' ) '
        return mdx
    

    def __part_order(self,cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter):

        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        for order in part_order:
            # mdx+= 'order('
            if  part_order[order]=='ASC' or part_order[order] == 'DESC' or part_order[order]=='BASC' or part_order[order] == 'BDESC' :
                
                mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows,part_order,part_filter)
                # mdx+=self.__order(cube,order,part_order)
            else:
                
                mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows,part_filter=part_filter)
                # mdx+= '<<{0} in order is incorrect >> '.format(part_order[order])
        return mdx



    def __filter(self,cube,part_filter,part_on_rows,range_rows,exclude_rows):
        mdx=''
        medidas=cube.medidas
        filtrada=False
        dimensiones=cube.dimensiones
        
        mdx+= 'filter( '
        mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows)+', '
        
        for filte in part_filter:
           
            #key=filte.keys()[0]
           
            if filtrada:
                mdx+=' and '
            if filte in dimensiones:
          
                dimension=dimensiones[filte]
                position=dimension.find('.')
                dimension=dimension[position+1:]
                position+=dimension.find('.')+1
                dimension=dimensiones[filte][:position]

                mdx+= dimension+'.&['+part_filter[filte]+']'

            elif key in medidas:
                mdx+= medidas[key]+filte[filte][0] + filte[filte][1]
            else:
                swslog('error','Failed MDX class','<<error in filter {0}>> '.format(str(filte)))
                mdx+='<<error in filter {0}>> '.format(str(filte))

            filtrada=True


        return mdx+'  ) '

    def __on_row(self,cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter):
        medidas=cube.medidas
        dimensiones=cube.dimensiones
        mdx=''
        if part_order :
            if len(part_order)==1:
                mdx+=self.__part_order(cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter)
            else:
                swslog('error','Failed MDX class','<< part_order must be like {0}>>'.format(str({('Measures','Calls'):'ASC'})))
                mdx+='<< part_order must be like {0}>>'.format(str({('Measures','Calls'):'ASC'}))
        else:
            # if part_filter:
                
            #     mdx+= self.__filter(cube,part_filter,part_on_rows,range_rows,exclude_rows)
                
            # else:   
            mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows,part_filter=part_filter)
        
        return mdx

    # Pasandole unos parametros se forma la mdx
    # [('client','client'),('client','id'),...] part_on_rows y part_on_columns del mismo tipo 
    # range rows= {('client','fechask'):[('value1'),('value2')]}
    # part_from un string indicando el nombre del cubo 
    # part_where {('cdrfint','fechask'):('20130101000000','20130125000000'),('client','id'):'54'...}
    # part_order {('measure','calls'):'ASC'} ASC , DESC , BASC , BDESC
    # part_filter {('measure','calls'):'>1000'}
    # NON_EMPTY es un boolean para indicar si se quiere ese campo  
    def __with_set_member_part(self,cube,part_rows=[],part_ranking=[]):
        mdx=''
        mdx+='WITH SET orderedDimension as topcount(['+part_rows[0][0]+'].['+part_rows[0][1]+'].['+part_rows[0][2]+'].members,100000000,['+part_ranking[2][0]+'].['+part_ranking[2][1]+'])'
        mdx+=' MEMBER ranking_medida as RANK(['+part_rows[0][0]+'].['+part_rows[0][1]+'].CurrentMember,orderedDimension)'
        return mdx

    def __select_rank(self,cube,part_rows=[],part_ranking=[]):
        mdx=''
        mdx+='select '
        
        if part_ranking[0]=="ASC":
            mdx+='bottomcount('
        else:
            mdx+='topcount('
        mdx+='orderedDimension,'+ part_ranking[1]+') on rows,'

        
        return mdx
    def __mdx_rank(self,cube,part_rows=[],part_columns=[],part_ranking=[],range_rows=[],exclude_rows=[]):
        mdx=''
        mdx+=self.__with_set_member_part(cube,part_rows,part_ranking);
        mdx+=self.__select_rank(cube,part_rows,part_ranking);
        mdx+= self.__rows_or_columns(cube,False,part_columns,range_rows,exclude_rows)
        mdx+=' on columns'
        return mdx
    def mdx (self,cube,part_rows=[],range_rows=[],exclude_rows={},part_columns=[],part_from='',part_where={},part_order=[],part_filter={},part_NON_EMPTY=True,total_data=False,request_data={},part_ranking=[]):
        
        """
          **Description:**
                This function is used to create the mdx which we will use to launch against the cube.
          **Args:**
                #. cube: An object cube which we have used to create the connection.
                #. part_rows: A list of tuples with three values to indicate the dimension to browse : [('client','client','client'),('client','id','all'),...]
                #. range_rows: A dict where we put the dimension which we want aplicate the range and like value the values of the range. 
                #. exclude_rows: A list of dict for the columns and value to exclude: [{('client','client'):2345},{('client','id'):...}]
                #. part_columns: A list of tuples for the columns to indicate the measures to browse: [('Measure','Calls'),('Measure','Attempts'),...]
                #. part_from  A string with the name of the cube :'[stoneworksolutions dev]'
                #. part_where:  A dict. The key is the dimension and the value is the value which want put in the where :{('client','client'):'Aryans',('cdrfint','fecha'):('2013101010101010','2013101110101010')....}
                #. part_order: A dict with only one key.The key is the measure or dimension to order and the value indicate the order to do, it can be('ASC','DESC','BASC','BDESC') :{('measure','calls'):'ASC'}
                #. part_filter: A dict with only one key.The key is the measure and the value is a string with the expression to filter : {('measure','calls'):(>,1000),...}
                #. part_NON_EMPTY: A booleann that indicate if is True that we want the clausule 'non empty' in the mdx , by contrast we don`t want non empty in the mdx
                #. total_data: A boolean. If it is true in the part rows will be put the dimension [Destination].[Destination].[Destination] only so the values will be gruped.
                #. part_ranking: A list with differents values. An example is part_rank=["ASC","10",('Measure','Calls')]. The first value indicates how we want the order, the second how many rows will be return and the third the measure on which will do the ranking.

          **Returns:**
                This function return a string which is a mdx.
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
              Nothing.
          Other information ::
        
        
        """
        #select
        ##MIRAR SI EN SELECT Y EN WHERE ESTA LA MISMA DIMENION DE SER ASI DEJARLA SOLO EL SELECT Y UTILIZAR FILTER
        # print 'antes: filtro ', part_filter,'rows',part_rows ,'where', part_where
        part_filter,part_where=self.__whereInSelect(part_where,part_rows,part_filter)
        mdx=''
        # print 'despues: filtro ', part_filter,'rows',part_rows ,'where', part_where
        part_rows=sorted(list(set(part_rows)))
        if cube.dimensiones:
            if part_ranking:
                mdx=self.__mdx_rank(cube,part_rows=part_rows,part_columns=part_columns,part_ranking=part_ranking,range_rows=range_rows,exclude_rows=exclude_rows)
            
            else: 
                mdx='select'
                mdx+= self.__non_empty(part_NON_EMPTY)
                
                # on rows
                if len(part_rows)>0:
                    
                    mdx+= self.__on_row(cube,part_rows,range_rows,exclude_rows,part_order,part_filter)
                    mdx+= 'on rows, '
                if total_data==True:
                    mdx='select non empty ([Destination].[Destination].[Destination])'
                    mdx+= 'on rows, '
                
                mdx+= self.__rows_or_columns(cube,False,part_columns,range_rows,exclude_rows)
                mdx+=' on columns'
                # on columns

            
            
   
            
            if part_where:
                # segunda_fecha=part_where[('Date','Id','Id')][1]
                # fecha=segunda_fecha[:8]
                # hora=segunda_fecha[8:]
                # fecha=str(int(fecha))
                # hora='235959'
                # part_where[('Date','Id','Id')]=(part_where[('Date','Id','Id')][0],fecha+hora)
                date_in_where=False
                date_in_rows=False
               
                

                for i in part_where.keys():
                    if 'Date' in i :
                        date_in_where=True
               
                for i in part_rows:
                    if (('Date' in i)|('Time' in i)) :
                        date_in_rows=True
                
                # print 'part_where es : ',date_in_where,'  y part_rows es  :  ',date_in_rows
                # print 'TE TE'*30
                # print date_in_rows
                # print date_in_where
                # print  date_in_rows and date_in_where
                # if date_in_rows and date_in_where:
                    
                tiempo={'Time':False,'Date':False}
                for i in part_where:
                    if i[0]in tiempo:
                        tiempo[i[0]]=i
                        dim_time=i
                
    
            
                if tiempo['Date']:
                    fecha_comienzo=int(part_where[dim_time][0][8:-2])==0
                    fecha_fin=int(part_where[dim_time][1][8:-2])==2359

                # print fecha_comienzo and fecha_fin
                
                if fecha_comienzo and fecha_fin:
                    #from 
                    mdx+=' from '+ part_from
                    #where
                    # print 'WHERE DICT 22222222222222222222222222222222'
                    mdx+=self.__where_dict2(cube,part_where,request_data)
                else:
                    # print '++++--'*32
                    mdx+=' from ('
                    #where
                    # print 'WHERE DICT 11111111111111111111111111111111111'
                    mdx+=self.__where_dict(cube,part_where,request_data)
                    mdx+=' '+part_from +' ) '
                # else:
                     #from 
                    # mdx+=' from '+ part_from
                    #where
                    # mdx+=self.__where_dict2(cube,part_where,request_data)
            else:
                #from 
                mdx+=' from '+ part_from
                #where

          
            return mdx
        else:
            swslog('error','Failed MDX class','cube has not dimensions or it is not good connect')
            return 'cube has not dimensions or it is not good connect'




    def __whereInSelect(self,part_where,part_rows,part_filter):
        # print 'dentro'
        dimensiones=[]
        for i in part_where:
            for j in part_rows:

                if i==j:
                    # print i , j ,'asdsadafsdfasdfsadf'
                    dimensiones.append(i)
        return self.__quitar_where_poner_filter(dimensiones,part_where,part_filter)


    def __quitar_where_poner_filter(self,dimensiones,part_where,part_filter):
        # print 'dentro'
        new_filter={}
        for dimension in dimensiones:
            valor_filter=part_where[dimension]
            # print 'value------where no modify',valor_filter , part_where
            del part_where[dimension]
            # print 'where modify',part_where
            new_filter[dimension]=valor_filter
            # print new_filter
        # print part_where
        return new_filter,part_where
        

    def select_for_filter(self,cube,on_rows=[],medida='',exclude_rows={}):

        """
          **Description:**
                This function is used only from the method filter and is used to create his select part.
          **Args:**
                #. cube: A cube instance.
                #. on_rows: A list whit the dimensions to use.
                #. medida: A string which indicate a measure to put.
          **Returns:**
                A string which is a mdx but only the select
          **Modify:**
                Nothing.
          **Raises:**
                Nothing.
          **Import**::
              Nothing.
          Other information ::
        
        """
        

        selects= cube.dimensiones
        select='select non empty'

        select+=self.__rows_or_columns(cube,True,part=on_rows,range_rows={},exclude_rows=exclude_rows)

        select+=' on rows, {'+medida+'} on columns '
        return select

################################################################################################################################################
################################################################################################################################################


