import os
import xml.etree.ElementTree as ET
from oqtoolsui.common.xml_utils import write_xml


def save(parameters, targetFile):
    f = open(targetFile, 'w')
    for key in parameters:
        line = key + '=' + parameters[key]
        f.write(line + '\n')

    f.flush()
    f.close()


def load(sourceFile):
    f = open(sourceFile, 'r')
    parameters = dict()
    for line in f.readlines():
        index = line.index('=')
        if index >= 0:
            parameters[line[:index].strip()] = line[index+1:].strip()
    
    f.close()
    return parameters


def execute(parameters, targetDir):
    if 'name' not in parameters or len(parameters['name'].strip()) == 0:
        raise Exception('Name parameter is empty')

    runName = parameters['name'].strip()
    newDir = os.path.join(targetDir, runName)

    if not os.path.exists(newDir):
        os.makedirs(newDir)

    jobIniContent = getJobIniContent(parameters, 'output/'+runName)
    writeGmpeLogicTree(os.path.join(newDir, 'gmpe_logic_tree.xml'), parameters['gmpes'])
    writeJobIni(os.path.join(newDir, 'job.ini'), jobIniContent)


def getJobIniContent(parameters, outDir):
    parentDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobIniFile = os.path.join(parentDir, 'oqtools/job.ini.template')
    intensityLevelsFile = os.path.join(parentDir, 'oqtools/intensityLevels.txt')

    with open(jobIniFile, 'r') as f:
        jobIniTemplate = f.read()

    with open(intensityLevelsFile, 'r') as f:
        intensityLevels = f.read()

    for prm in parameters:
        key = '[['+str(prm)+']]'

        if key in jobIniTemplate:
            jobIniTemplate = jobIniTemplate.replace(key, parameters[prm])

    if 'periods' in parameters:
        periodStr = '{'
        periodList = list()

        for period in parameters['periods'].split(' '):
            period = float(period.strip())
            if period == 0.0:
                inner_period_str = '"PGA"'
            else:
                inner_period_str = '"SA(' + str(period) + ')"'

            inner_period_str += ': ' + intensityLevels
            periodList.append(inner_period_str)

        periodStr += ','.join(periodList)
        periodStr += '}'

        jobIniTemplate = jobIniTemplate.replace('[[intensity_levels]]', periodStr)

    jobIniTemplate = jobIniTemplate.replace('[[export_dir]]', outDir)
    return jobIniTemplate


def writeJobIni(filePath, jobIniContent):
    f = open(filePath, 'w')
    f.write(jobIniContent)
    f.flush()
    f.close()


def writeGmpeLogicTree(targetFilePath, gmpes):
    nrml_node = ET.Element('nrml')
    nrml_node.set('xmlns', 'http://openquake.org/xmlns/nrml/0.4')

    logic_tree_node = ET.SubElement(nrml_node, 'logicTree')
    logic_tree_node.set('logicTreeID', 'lt1')

    logic_tree_branching_level_node = ET.SubElement(logic_tree_node, 'logicTreeBranchingLevel')
    logic_tree_branching_level_node.set('branchingLevelID', 'bl1')

    logic_tree_branch_set_node = ET.SubElement(logic_tree_branching_level_node, 'logicTreeBranchSet')
    logic_tree_branch_set_node.set('uncertaintyType', 'gmpeModel')
    logic_tree_branch_set_node.set('branchSetID', 'bs1')
    logic_tree_branch_set_node.set('applyToTectonicRegionType', 'Active Shallow Crust')

    for i in range(len(gmpes)):
        logic_tree_branch_node = ET.SubElement(logic_tree_branch_set_node, 'logicTreeBranch')
        logic_tree_branch_node.set('branchID', 'b' + str(i+1))

        uncertainty_model_node = ET.SubElement(logic_tree_branch_node, 'uncertaintyModel')
        uncertainty_model_node.text = gmpes[i].name

        uncertainty_weight_node = ET.SubElement(logic_tree_branch_node, 'uncertaintyWeight')
        uncertainty_weight_node.text = str(gmpes[i].weight)

    tree = ET.ElementTree(nrml_node)
    write_xml(tree, targetFilePath)