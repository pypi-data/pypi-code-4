# Based on pygments documentation
from __future__ import print_function
from pygments.lexer import RegexLexer, include
from pygments.lexers import PythonLexer
from pygments.token import *

class AslLexer(RegexLexer):
    name = 'ASL'
    aliases = ['asl']
    filenames = ['*.asl', '*.aml']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'[^\S\n]+', Text),
            (r'//.*$', Comment),
            (r'[{}(),]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            include('keywords'),
            include('operators'),
            include('string'),
            include('name'),
            include('numbers'),
        ],
        'keywords':[
            (r'AttribQuick|AttribSendReceive|AttribByte|AttribBytes|AttribRawBytes|'
             r'AttribRawProcessBytes|AttribWord|AttribBlock|AttribProcessCall|AttribBlockProcessCall|'
             r'AnyAcc|ByteAcc|WordAcc|DWordAcc|QWordAcc|BufferAcc|AddressRangeMemory|'
             r'AddressRangeReserved|AddressRangeNVS|AddressRangeACPI|RegionSpaceKeyword|'
             r'FFixedHW|PCC|AddressingMode7Bit|AddressingMode10Bit|DataBitsFive|DataBitsSix|'
             r'DataBitsSeven|DataBitsEight|DataBitsNine|BusMaster|NotBusMaster|ClockPhaseFirst|'
             r'ClockPhaseSecond|ClockPolarityLow|ClockPolarityHigh|SubDecode|PosDecode|BigEndianing|'
             r'LittleEndian|AttribBytes|AttribRawBytes|AttribRawProcessBytes|FlowControlNone|'
             r'FlowControlXon|FlowControlHardware|Edge|Level|ActiveHigh|ActiveLow|ActiveHigh|'
             r'ActiveLow|ActiveBoth|Decode16|Decode10|IoRestrictionNone|IoRestrictionInputOnly|'
             r'IoRestrictionOutputOnly|IoRestrictionNoneAndPreserve|Lock|NoLock|'
             r'MTR|MEQ|MLE|MLT|MGE|MGT|MaxFixed|MaxNotFixed|Cacheable|WriteCombining|Prefetchable|'
             r'NonCacheable|MinFixed|MinNotFixed|UnknownObj|IntObj|StrObj|BuffObj|PkgObj|FieldUnitObj|'
             r'DeviceObj|EventObj|MethodObj|MutexObj|OpRegionObj|PowerResObj|ProcessorObj|'
             r'ThermalZoneObj|BuffFieldObj|DDBHandleObj|ParityTypeNone|ParityTypeSpace|ParityTypeMark|'
             r'ParityTypeOdd|ParityTypeEven|PullDefault|PullUp|PullDown|PullNone|PolarityHigh|'
             r'PolarityLow|ISAOnlyRanges|NonISAOnlyRanges|EntireRange|ReadWrite|ReadOnly|'
             r'UserDefRegionSpace|SystemIO|SystemMemory|PCI_Config|EmbeddedControl|SMBus|SystemCMOS|'
             r'PciBarTarget|IPMI|GeneralPurposeIO|GenericSerialBus|ResourceConsumer|ResourceProducer|'
             r'Serialized|NotSerialized|Shared|Exclusive|SharedAndWake|ExclusiveAndWake|'
             r'ControllerInitiated|DeviceInitiated|StopBitsZero|StopBitsOne|StopBitsOnePlusHalf|'
             r'StopBitsTwo|Width8Bit|Width16Bit|Width32Bit|Width64Bit|Width128Bit|Width256Bit|'
             r'SparseTranslation|DenseTranslation|TypeTranslation|TypeStatic|Preserve|WriteAsOnes|'
             r'WriteAsZeros|Transfer8|Transfer16|Transfer8_16|ThreeWireMode|FourWireMode', Keyword),
        ],
        'operators': [
            (r'AccessAs|Acquire|Add|Alias|And|Arg0|Arg1|Arg2|Arg3|Arg4|Arg5|Arg6|'
             r'BankField|Break|BreakPoint|Buffer|Case|Concatenate|ConcatenateResTemplate|'
             r'CondRefOf|Connection|Continue|CopyObject|CreateBitField|CreateByteField|'
             r'CreateDWordField|CreateField|CreateQWordField|CreateWordField|DataTableRegion|'
             r'Debug|Decrement|Default|DefinitionBlock|DerefOf|Device|Device|Divide|DMA|'
             r'DWordIO|DWordMemory|DWordSpace|EisaId|ElseIf|Else|EndDependentFn|Event|'
             r'ExtendedIO|ExtendedMemory|ExtendedMemory|ExtendedSpace|External|Fatal|Field|'
             r'FindSetLeftBit|FindSetRightBit|FixedDMA|FixedIO|FromBCD|Function|GpioInt|GpioIo|'
             r'I2CSerialBus|If|Include|Increment|Index|IndexField|Interrupt|IO|IRQNoFlags|IRQ|'
             r'LAnd|LEqual|LGreater|LGreaterEqual|LLess|LLessEqual|LNotEqual|LNot|Load|LoadTable|'
             r'Local0|Local1|Local2|Local3|Local4|Local5|Local6|Local7|LOr|Match|Memory24|'
             r'Memory32|Memory32Fixed|Method|Mid|Mod|Multiply|Mutex|Name|NAnd|NoOp|NOr|Not|'
             r'Notify|Offset|ObjectType|Ones|One|OperationRegion|Or|Package|PowerResource|'
             r'Processor|QWordIO|QWordMemory|QWordSpace|RawDataBuffer|RefOf|Register|Release|'
             r'Reset|ResourceTemplate|Return|Revision|Scope|ShiftLeft|ShiftRight|Signal|SizeOf|'
             r'Sleep|SPISerialBus|Stall|StartDependentFn|StartDependentFnNoPri|Store|Subtract|'
             r'Switch|ThermalZone|Timer|ToBCD|ToBuffer|ToDecimalString|ToHexString|ToInteger|'
             r'ToString|ToUUID|UARTSerialBus|Unicode|Unload|VendorLong|VendorShort|Wait|While|'
             r'WordBusNumber|WordIO|WordSpace|XOr|Zero', Operator),
        ],
        'builtins': [
        ],
        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'0[0-7]+j?', Number.Oct),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+j?', Number.Integer)
        ],
        'name': [
            ('[a-zA-Z_][a-zA-Z0-9_]{0,3}', Name),
        ],
        'string': [
            (r'"[^\\"\n]*"', String),
        ],
    }
