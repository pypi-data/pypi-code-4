#! /usr/bin/env python

import random

class PatternGenerator:
    """
    Generates a byte array of given length with fixed values, random data or running byte sequence.
    A start offset, minimum and maximum value of the running byte sequence can be changed by parameters.
    All pattern types support 2 bytes of pattern length in front which can be switched on and off.
    
    Example:

    patGen = PatternGenerator()
    patGen.set_random(True, 10)
    data = patGen.get_data_pattern()
    for i in data:
    print(hex(i))
    
    patGen.set_value(True, 1024, 0xaa)
    data = patGen.get_data_pattern()
    for i in data:
    print(hex(i))

    patGen.set_running_byte(False, True, 1, minValue=0x00, maxValue=0x1F)
    for i in range(20):
        print("Data",i+1)
        data = patGen.get_data_pattern(numData = i+1)
        for i in data:
            print (hex(i))
    """
    
    _patternType = 'RunningByte'
    _addLength = False
    _addStartOffset = False
    _numData = 1
    _minValue = 0x00
    _maxValue = 0xFF
    _startOffset = 0x00
    
    def __init__(self):
        pass
         
    def set_random(self, addLength, numData):
        self._patternType = 'Random'  
        self._addLength = addLength
        self._numData = numData
        
    def set_value(self, addLength, numData, value):
        self._patternType = 'Value'
        self._addLength = addLength
        self._numData = numData
        self._minValue = value
        
    def set_running_byte(self, addLength, addStartOffset, numData, minValue, maxValue):
        self._patternType = 'RunningByte'
        self._addLength = addLength
        self._addStartOffset = addStartOffset
        self._numData = numData
        self._minValue = minValue
        self._maxValue = maxValue
        self._startOffset = 0x00
        
    def get_data_pattern(self, patternType=None, addLength=None, addStartOffset=None, numData=None, minValue=None, maxValue=None):
        if patternType == None:
            patternType = self._patternType
        if addLength == None:
            addLength = self._addLength 
        if addStartOffset == None:
            addStartOffset = self._addStartOffset    
        if numData == None:
            numData = self._numData
        if minValue == None:
            minValue = self._minValue
        if maxValue == None:
            maxValue = self._maxValue
            
        if patternType == 'Random':
            return self._generate_random_pattern(addLength, numData, minValue, maxValue)
            
        elif patternType == 'Value':
            return self._generate_value_pattern(addLength, numData, minValue)
        
        elif patternType == 'RunningByte':
            return self._generate_running_byte_pattern(addLength, addStartOffset, numData, minValue, maxValue)
        
        else:
            pass 
    
    def _generate_random_pattern(self, addLength, numData, minValue, maxValue):
        """
        Generates a random byte pattern
        
        addLength - If True, 2 bytes of data length will be set in front of the pattern
        numData - Number of pattern bytes
        minValue / maxValue - Random pattern bytes will be generated in range from minValue to maxValue     
        """
        if addLength:
            length = bytearray.fromhex("{0:04x}".format(numData))
            for lengthByte in length:
                yield lengthByte
        for _ in range(numData):
            yield random.randrange(minValue, maxValue)
                
    def _generate_value_pattern(self, addLength, numData, value):
        """
        Generates a pattern which is filled with the given value
        
        addLength - If True, 2 bytes of data length will be set in front of the pattern
        numData - Number of pattern bytes
        value - All pattern bytes will be filled with this value
        """
        if addLength:
            length = bytearray.fromhex("{0:04x}".format(numData))
            for lengthByte in length:
                yield lengthByte
        for _ in range(numData):
            yield value
    
    def _generate_running_byte_pattern(self, addLength, addStartOffset, numData, minValue, maxValue):
        """
        Generates a running byte pattern (incremented byte)
        A start offset is saved and will be added to the beginning value of the pattern on the next method call
        
        addLength - If True, 2 bytes of data length will be set in front of the pattern
        numData - Number of pattern bytes
        minValue / maxValue - Pattern bytes will be generated in range from minValue to maxValue     
        """
        byteNum = 0
        
        #Generate length bytes
        if addLength:
            length = bytearray.fromhex("{0:04x}".format(numData))
            for lengthByte in length:
                yield lengthByte
                
        if addStartOffset:
            #First part of data pattern, minValue is incremented by startOffset
            if (maxValue - minValue - self._startOffset) < (numData - byteNum):
                #Full value range reduced by startOffset fits to remaining pattern space
                for value in range(minValue + self._startOffset, maxValue + 1):
                        yield value
                        byteNum += 1
            else:
                #Value range reduced by startOffset does not fit and must be reduced to remaining pattern space
                for value in range(minValue + self._startOffset, minValue + self._startOffset + (numData - byteNum)):
                        yield value
                        byteNum += 1
                        
            if self._startOffset == maxValue:
                self._startOffset = 0
            else:
                self._startOffset += 1
                
        #Further loops of full data range from minValue to maxValue                      
        while byteNum < numData:
            if (maxValue - minValue) <= (numData - byteNum -1):
                #Full value range fits to remaining pattern space 
                for value in range(minValue, maxValue + 1):
                    yield value
                    byteNum += 1
            else:
                #Value range does not fit and must be reduced to remaining pattern space
                for value in range(minValue, minValue + (numData - byteNum)):
                    yield value
                    byteNum += 1
            

