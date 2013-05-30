import log
import Check
import re
import ConfigParser
import xlrd
from xlrd import open_workbook

class HyperlinkError(Exception):
    pass
    
class Excel:

    def __init__(self,debug=False):             
        self.configure()
        self.debug = debug
            
    def configure(self):
        cf = ConfigParser.ConfigParser()
        cf.read("config.conf")      
        file_name = cf.get("EXCEL","File_name")
        self.work_book = open_workbook(file_name)
        sheet_index = cf.getint("EXCEL", "Table_sheet")
        self.table_sheet = self.work_book.sheet_by_index(sheet_index)
        self.table_col = cf.getint("EXCEL", "Table_col")            
        self.Instance_col = cf.getint("EXCEL", "Instance_col")      
        self.tag_name_col = int(cf.get("EXCEL", "tag_name_col"))
        self.range_col = int(cf.get("EXCEL", "range_col"))
        self.words_col = int(cf.get("EXCEL", "words_col"))
        
    def update(self,row):
        self.log.info("Update row: %s"%row)
        self.instance = self.get_instance(row)
        if self.instance == "NA" or self.instance == "" or re.match(r'\D+',self.instance):
            self.log.info("Finished.\n")
            return False
        else:
            self.target_sheet = self.get_sheet(row)
            self.words = self.get_words(self.words_col,row)
            self.type = self.get_type()
            self.range = self.get_range(self.get_section(row))
            self.log.info("Updata finished.\n")
            return True
        
    def get_instance(self, row):
        instance = str(self.table_sheet.cell(row,self.Instance_col).value)
        self.log.info("Instance: %s"%instance)
        return instance
    
    def get_model_col(self,model_name):
        for col in range(self.table_sheet.ncols):
            if str(self.table_sheet.cell(0,col).value) == model_name:
                self.log.debug("Ok, I find %s in column %s !"%(model_name, col))
                self.model_col = col
                return col
            else:
                self.log.debug("I'm looking for Model %s, but this is %s"%(model_name,\
                                str(self.table_sheet.cell(0,col).value)))       
        self.log.error("No model info, stop!")
        
    def model_check(self, row):     
        self.log.info("Model check: %s"%str(self.table_sheet.cell(row, self.model_col).value))
        if self.debug:
            return True
        elif str(self.table_sheet.cell(row, self.model_col).value) == "X":
            return True
        else:
            return False
    
    def get_words(self, size_col,row):      
        if row > 0:
            words = self.table_sheet.cell(row, size_col).value
            self.log.info("Word: %s"%words)
            return words
        
    def get_sheet(self, row):
        hyperlink = self.table_sheet.hyperlink_map[row,self.table_col]
        target_sheet_name = str(hyperlink.textmark)
        target = ''
        for i in target_sheet_name:
            if i == "!":
                break
            target = target + i 
        self.log.info("Target Sheet Name:%s"%target)
        try:
            target_sheet = self.work_book.sheet_by_name(target)
        except xlrd.XLRDError:
            self.log.error("Can't open sheet '%s'"%target)
        return target_sheet
    
    def get_section(self,row):
        section = self.table_sheet.cell(row,self.table_col).value
        match = re.match(r".*\((.+)\)",str(section))
        if match:
            section = match.group(1)
        else:
            section = ""
        return section
            

    def get_tag_name(self, serial_num):
        tag_name = str(self.target_sheet.cell(serial_num+2, self.tag_name_col).value)   
        return tag_name
        
    def get_range(self,section=''): #getData
        li=[]
        if section:
            self.log.debug("SEE:%s",section)
            section = re.match(r"(.*) *(to) *(\d+)",section)
            begin = section.group(1)
            end = section.group(3)
            if re.match(r"DC",begin):
                begin = 2
            else:   
                begin = int(begin) + 2
            end = int(end) + 2
        else:   
            begin = 2
            end = self.target_sheet.nrows
        for row in range(begin, end ):
            # if row == 2:
                # firstLine = self.target_sheet.cell(row,self.range_col).value 
                # pattern = re.compile(r'0=')
                # if pattern.search(str(firstLine)):
                    # if not hasRecord:
                        # return False
                    # else:
                        # pass
                # else:
                    # pass
            if self.type == "Int16":
                type = self.target_sheet.cell(row, self.type_col).value 
                if re.match(r'Bit\d*', type ) or re.match(r'bit\d*', type ):
                    self.log.debug("Bit Type: %s"%type)
                    pass
                else:
                    range_value = self.target_sheet.cell(row, self.range_col).value
                    li.append(range_value)     
                    self.log.debug("range:%s"%range_value)
            else:
                range_value = self.target_sheet.cell(row, self.range_col).value
                li.append(range_value)
                self.log.debug("range:%s"%range_value)
        return li
    
    def get_type_col(self):
        col_v = 1000
        for col in range(self.target_sheet.ncols):
            if str(self.target_sheet.cell(1, col).value) == "Type":
                self.type_col = col
        if self.type_col == 1000:
            self.log.error("Get data exception 3: Not Find 'type'")
            
    def get_type(self): 
        self.get_type_col()
        value_type = str(self.target_sheet.cell(2,self.type_col).value)
        self.data_type = value_type
        self.log.info("Data type: %s" %value_type)
        return value_type
        
    def get_byte_info(self):
        li=[]
        for col in range(self.target_sheet.ncols):
            if str(self.target_sheet.cell(1, col).value) == "Start Byte":
                for row in range(2, self.target_sheet.nrows):
                    aa = self.target_sheet.cell(row, col).value
                    bb = self.target_sheet.cell(row, col+1).value
                    if aa != ''and bb != '':
                        bb = str(bb)
                        li.append(bb)
                return li       