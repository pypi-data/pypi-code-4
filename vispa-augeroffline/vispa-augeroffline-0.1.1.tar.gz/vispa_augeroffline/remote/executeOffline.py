#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree as ET
import argparse
import os
import subprocess
import shlex


''' parse command line arguments '''
parser = argparse.ArgumentParser(description='Generate EventFileReader.xml out of command line options.')
parser.add_argument('--dataFiles', dest='data_files', metavar='file1', type=str, nargs='+', help='list of data files')

parser.add_argument('-b', dest='bootstrap', metavar='/path/to/bootstrap.xml', type=str, nargs=1, help='bootstrap.xml file')

parser.add_argument('--fileType', metavar='filetype', dest='data_file_type', nargs=1, help='input file type, choose between Offline FDAS CDAS IoAuger CORSIKA CONEX CONEXRandom AIRES SENECA REAS RadioSTAR RadioMAXIMA RadioAERA ')

parser.add_argument('--outputPath', dest='output_path', metavar='/output/path/', type=str, nargs=1, help='output path')

parser.add_argument('--outputFileName', dest='output_file_name', metavar='ADST.root', type=str, nargs=1, help='filename of ADST output file')

parser.add_argument('--userAugerOffline', dest='user_auger_offline', metavar='./userAugerOffline', type=str, nargs=1, help='path to offline executable')

parser.add_argument('--uuid', dest='uuid', metavar='jobid', type=str, default='1', nargs=1, help='the job uuid')

args = vars(parser.parse_args())
data_file_type=args['data_file_type'][0]
data_files = args['data_files']
bootstrap_path = args['bootstrap'][0]
output_path = args['output_path'][0]
output_file_name = args['output_file_name'][0]
user_auger_offline = args['user_auger_offline'][0]
_uuid = args['uuid'][0]

print "outputpath: ", output_path

''' create bootstrap_uuid.xml with new link to EventFileReader '''
parser = ET.XMLParser(remove_blank_text=True, remove_comments=True, attribute_defaults=False, recover=True, resolve_entities=False)
BootstrapTree = ET.parse(bootstrap_path, parser)
BootstrapRoot = BootstrapTree.getroot()
docinfo = BootstrapTree.docinfo

config_link_event = BootstrapRoot.find(".//configLink[@id='EventFileReader']")
#-------------------------------------- create config link if it does not exists
if(config_link_event is None):
    config_link_event = ET.SubElement(BootstrapRoot.find("./centralConfig"),"configLink")
    config_link_event.set("id", "EventFileReader")
    config_link_event.set("type", "XML")
    
XLINK_NAMESPACE = "http://www.auger.org/schema/types"
XLINK = "{%s}" % XLINK_NAMESPACE

XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI = "{%s}" % XSI_NAMESPACE

config_link_event.set(XLINK+"href",os.path.join(output_path,"EventFileReader_"+str(_uuid)+".xml"))

offline_config_path = BootstrapRoot.get(XSI+"noNamespaceSchemaLocation")[:-14]

#------------------------------------------- change output path of RecDataWriter
bootstrap_rec_data_writer = BootstrapRoot.find(".//configLink[@id='RecDataWriter']")
boostrap_output_file_name = bootstrap_rec_data_writer.find(".//outputFileName")
print boostrap_output_file_name.text
boostrap_output_file_name.text = os.path.join(output_path, output_file_name)

fBootstrap = open(os.path.join(output_path,"bootstrap_"+str(_uuid)+".xml"),"w")
fBootstrap.write(ET.tostring(BootstrapTree,pretty_print=True, xml_declaration=True, encoding=docinfo.encoding))
fBootstrap.close()



''' create EventFileReader.xml '''
eventFileReaderRoot = ET.fromstring('<?xml version="1.0" encoding="iso-8859-1"?><EventFileReader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="'+os.path.join(offline_config_path,'EventFileReader.xsd')+'"><InputFileType></InputFileType><InputFilenames></InputFilenames></EventFileReader>')
EventFileReaderTree = eventFileReaderRoot.getroottree()

eventFileReaderRoot.find("./InputFileType").text = data_file_type
filenames_tag = eventFileReaderRoot.find("./InputFilenames")
for filename in data_files:
    if(filenames_tag.text is None):
        filenames_tag.text = "\n\t"+ filename +"\n"
    else:
        filenames_tag.text = filenames_tag.text + "\t"+ filename +"\n"

docinfo = EventFileReaderTree.docinfo
fEventFileReader = open(os.path.join(output_path,"EventFileReader_"+str(_uuid)+".xml"),"w")
fEventFileReader.write(ET.tostring(EventFileReaderTree,pretty_print=True, xml_declaration=True, encoding=docinfo.encoding))
fEventFileReader.close()

cmd = shlex.split(user_auger_offline+" -b "+os.path.join(output_path,"bootstrap_"+str(_uuid)+".xml"))
popen = subprocess.Popen(cmd, stdout = subprocess.PIPE)
popen.wait()
