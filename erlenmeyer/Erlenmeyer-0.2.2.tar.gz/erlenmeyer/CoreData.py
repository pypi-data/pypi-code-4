#
#  CoreData.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 6, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
import os
from xml.dom import minidom
    
class CoreData (dict):
    """
    A dictionary parsed from an .xcodedatamodeld file.
    """
    
    # initializers
    def __init__(self, coreDataFile, primaryKey = 'uuid'):
        """
        DOCME
        """
    
        coreDataFile = '%s/%s/contents' % (coreDataFile, os.path.basename(coreDataFile[:-1]))
        coreDataMinidom = minidom.parse(open(coreDataFile))
        minidomList = self.__listFromMinidom(coreDataMinidom)
        self.__parseFromMinidomList(minidomList, primaryKey)
        
    # accessors
    def __dictFromMinidomNode(self, minidomNode):
        """
        DOCME
        """
        
        minidomDict = {}
        if minidomNode.attributes:
            for attributeIndex in range(minidomNode.attributes.length):
                attribute = minidomNode.attributes.item(attributeIndex)
                minidomDict[attribute.name] = attribute.value
            
        if minidomNode.childNodes:
            minidomDict[minidomNode.nodeName] = []
            for childNode in minidomNode.childNodes:
                childNodeDict = self.__dictFromMinidomNode(childNode)
                if childNodeDict:
                    minidomDict[minidomNode.nodeName].append(childNodeDict)
        
        return minidomDict
        
    def __listFromMinidom(self, minidomObject):
        """
        DOCME
        """
        
        list = []
        if minidomObject.childNodes:
            for childNode in minidomObject.childNodes:
                childNodeDict = self.__dictFromMinidomNode(childNode)
                if childNodeDict:
                    list.append(childNodeDict)
                    
        return list
        
    def __modelForMinidomDict(self, minidomDict, minidomList, primaryKey):
        model = {
            "className": minidomDict['name'],
            "parentClassName": "database.Model",
            "primaryKey": primaryKey,
            "primaryKeyType": None,
            "attributes": [],
            "relationships": []
        }
        
        if 'parentEntity' in minidomDict:
            model['parentClassName'] = minidomDict['parentEntity']
        
        # Add properties
        if 'entity' in minidomDict:
            for propertyDict in minidomDict['entity']:
                if 'attributeType' in propertyDict:
                    model['attributes'].append(self.__attributeForMinidomDict(propertyDict))
                else:        
                    model['relationships'].append(self.__relationshipForMinidomDict(propertyDict, minidomList, primaryKey))
                 
        # Add parent properties   
        parentDict = self.__parentDictForMinidomDictInMinidomList(minidomDict, minidomList)
        while parentDict:
            for propertyDict in parentDict['entity']:
                if 'attributeType' in propertyDict:
                    model['attributes'].append(self.__attributeForMinidomDict(propertyDict))
                else:
                    model['relationships'].append(self.__relationshipForMinidomDict(propertyDict, minidomList, primaryKey))
                    
            parentDict = self.__parentDictForMinidomDictInMinidomList(parentDict, minidomList)
               
        # Find primary key type     
        for attribute in model['attributes']:
            if attribute['name'] == primaryKey:
                model['primaryKeyType'] = attribute['type']
                break
        
        return model
        
    def __attributeForMinidomDict(self, minidomDict):
        attribute = {
            "name": minidomDict['name'],
            "type": "String(256)",
            "exampleValue": "some_%s" % (minidomDict['name'])
        }
        
        if minidomDict['attributeType'] == "Integer":
            attribute['type'] = "Integer"
            attribute['exampleValue'] = "0"
        elif minidomDict['attributeType'] in ["Decimal", "Double", "Float"]:
            attribute['type'] = "Float"
            attribute['exampleValue'] = "0.0"
        elif minidomDict['attributeType'] == "Boolean":
            attribute['type'] = "Boolean"
            attribute['exampleValue'] = "false"
            
        return attribute
        
    def __relationshipForMinidomDict(self, minidomDict, minidomList, primaryKey):
        relationship = {
            "name": minidomDict['name'],
            "className": minidomDict['destinationEntity'],
            "inverseName": minidomDict['inverseName'],
            "inverseClassName": minidomDict['inverseEntity'],
            "isToMany": False,
            "inverseIsToMany": False,
            "hasBeenAccountedFor": False,
            "exampleValue": "%s_%s" % (minidomDict['name'], primaryKey)
        }
        
        if 'toMany' in minidomDict:
            relationship['isToMany'] = minidomDict['toMany'] == "YES"
        
        if 'hasBeenAccountedFor' in minidomDict:
            relationship['hasBeenAccountedFor'] = minidomDict['hasBeenAccountedFor']
        
        for inverseModelDict in minidomList[0]['model']:
            if 'name' not in inverseModelDict:
                continue
        
            if inverseModelDict['name'] == relationship['inverseClassName']:
                for inversePropertyDict in inverseModelDict['entity']:
                    if inversePropertyDict['name'] == relationship['inverseName']:
                        if 'toMany' in inversePropertyDict:
                            relationship['inverseIsToMany'] = inversePropertyDict['toMany'] == "YES"
                            inversePropertyDict['hasBeenAccountedFor'] = True
                            break
                else:
                    continue
                break
                
        return relationship
        
    def __parentDictForMinidomDictInMinidomList(self, minidomDict, minidomList):
        if 'parentEntity' not in minidomDict:
            return None
        
        for parentModelDict in minidomList[0]['model']:
            if 'name' not in parentModelDict:
                continue
            
            if parentModelDict['name'] == minidomDict['parentEntity']:
                return parentModelDict  
        else:
            return None 
    
    # mutators
    def __parseFromMinidomList(self, minidomList, primaryKey):
        """
        DOCME
        """
        
        self['models'] = []
        for modelDict in minidomList[0]['model']:
            if 'name' not in modelDict:
                continue
        
            if ('isAbstract' in modelDict) and (modelDict['isAbstract'] == "YES"):
                continue
        
            self['models'].append(self.__modelForMinidomDict(modelDict, minidomList, primaryKey))