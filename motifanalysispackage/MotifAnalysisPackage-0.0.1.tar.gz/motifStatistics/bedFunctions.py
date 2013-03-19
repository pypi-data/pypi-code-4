#################################################################################################
# Functions performed on bed files.
#################################################################################################

#################################################################################################
##### LIBRARIES #################################################################################
#################################################################################################

import os
import util
import random
import constants

#################################################################################################
##### FUNCTIONS #################################################################################
#################################################################################################

def createRandomCoordinates(coordDict, chromSizesLocation, prop=1.0):
    """Creates random coordinates based on coordDict coordinates.

    Keyword arguments:
    coordDict -- Coordinate dictionary to base the random coordinate creation.
    chromSizesLocation -- Location + name of the file containing the chromosome sizes.
    prop -- Proportion of coordDict coordinates to create the random coordinates.

    Returns:
    randDict -- Dictionary of random coordinates.
    """

    # Reading chrom sizes
    chromSizesFile = open(chromSizesLocation,"r")
    chromSizesDict = dict()
    for line in chromSizesFile:
        ll = line.strip().split("\t")
        chromSizesDict[ll[0]] = int(ll[1])
    chromSizesFile.close()

    # Creating list from coordDict
    coordList = []
    for k in coordDict.keys():
        for e in coordDict[k]: coordList.append([k]+e)

    # Creating random coordinates
    counter = 0
    randDict = dict()
    for k in coordDict.keys(): randDict[k] = []
    while(counter < len(coordList)*prop):
        chrName = coordList[counter%len(coordList)][0]
        pos1 = coordList[counter%len(coordList)][1]
        pos2 = coordList[counter%len(coordList)][2]
        coordLen = pos2 - pos1
        r = random.randint(0,chromSizesDict[chrName]-coordLen-1)
        randDict[chrName].append(coordList[counter%len(coordList)][1:])
        randDict[chrName][-1][0] = r
        randDict[chrName][-1][1] = r+coordLen
        randDict[chrName][-1][2] = "."
        randDict[chrName][-1][3] = 0
        counter += 1
    return randDict

def createBedDictFromSingleFile(coordFileName, separator=" ", features=[]):
    """Creates a dictionary from a coordinate (bed or pk) which keys are the chromossomes and 
       the elements are lists of selected bed features.

    Keyword arguments:
    coordFileName -- Location + name of the bed or pk file.
    separator -- Character used to separate the features in the bed or pk file. (default " ")
    features -- List containing the features positions to store. If empty (default), stores all features.

    Returns:
    coordDict -- Dictionary of bed items indexed by chromosome.
    """

    # Creating bed dictionary
    coordFile = open(coordFileName,"r")
    coordDict = dict()
    for line in coordFile:
        lineList = line.strip().split(separator)
        chrName = lineList[0]
        if(not features): feats = lineList[1:]
        else: feats = [lineList[i] for i in features]
        for i in range(0,len(feats)):
            if(util.instanceof(feats[i],"int")): feats[i] = int(feats[i])
            elif(util.instanceof(feats[i],"float")): feats[i] = float(feats[i])
        while(len(feats) < 5): feats.append(".") # Inserting features for bed6
        if(len(feats) > 5): feats = feats[:5] # Removing features for bed6
        if(chrName not in coordDict.keys()): coordDict[chrName] = [feats]
        else: coordDict[chrName].append(feats)      
    coordFile.close()
    return coordDict

def separateEvidence(inputDict):
    """Receives a dict and outputs two dictionaries. The second one contains "." in the NAME field and the
       first one contains everything else but ".".

    Keyword arguments:
    inputDict -- Input dictionary of bed entries.

    Returns:
    outputEvidence -- Dictionary of bed items containing everything but "." in the NAME field.
    outputNonEvidence -- Dictionary of bed items containing "." in the NAME field.
    """
    
    # Creating output dictionaries
    outputEvidence = dict([(e,[]) for e in inputDict.keys()])
    outputNonEvidence = dict([(e,[]) for e in inputDict.keys()])

    # Separating by evidence
    for k in inputDict.keys():
        for e in inputDict[k]:
            genes = e[2].split(":")
            containsEnriched = False
            for g in genes:
                if(g[0] != "."): 
                    containsEnriched = True
                    break
            if(containsEnriched): outputEvidence[k].append(e)
            else: outputNonEvidence[k].append(e)
    return outputEvidence, outputNonEvidence

def bedToBigBed(inputBedFileName, chromSizesLocation, outputBedFileName, removeBed=False):
    """Converts a bed file to a big bed (bb) file.

    Keyword arguments:
    inputBedFileName -- Input bed file location + name.
    chromSizesLocation -- Location + name of the chromosome sizes file.
    outputBedFileName -- Output bed file location + name.
    removeBed -- Wether to remove the initial bed file or not.

    Returns:
    outputBedFileName -- Big bed file.
    """
    os.system("bedToBigBed "+inputBedFileName+" "+chromSizesLocation+" "+outputBedFileName+" -verbose=0")
    if(removeBed): os.system("rm "+inputBedFileName)
    return 0

def printBedDict(bedDict, chromSizesLocation, outputBedFileName, out="bed", separator="\t"):
    """Print the contents of a bed dictionary on a bed or big bed file.

    Keyword arguments:
    bedDict -- Input bed dictionary.
    chromSizesLocation -- Location + name of the chromosome sizes file.
    outputBedFileName -- Output bed file location + name.
    out -- The type of file to print. Can be 'bed' or 'bb'. (default 'bed')
    separator -- The type of file to print. Can be 'tab' or 'space'. (default 'tab')

    Returns:
    outputBedFileName -- Resulting bed or big bed file.
    """
    if(out == "bed"): outFile = open(outputBedFileName,"w")
    elif(out == "bb"): outFile = open(outputBedFileName+"temp","w")
    for k in constants.getChromList(reference=[bedDict]):
        for e in bedDict[k]: outFile.write("\t".join([k]+[str(m) for m in e])+"\n")
    outFile.close()
    if(out == "bb"): bedToBigBed(outputBedFileName+"temp", chromSizesLocation, outputBedFileName, removeBed=True)
    return 0


