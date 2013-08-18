from pyivi.ivifactory import register_wrapper
from pyivi.ivicom import IviComWrapper
from pyivi.ivicom.ivicomwrapper import  FieldsClass, \
                                        pick_from_session
from pyivi.common import add_sc_fields_enum, \
                         ShortCut, \
                         add_sc_fields

from collections import OrderedDict
from numpy import array, double, linspace

class Acquisition(FieldsClass):
    _pickup = [  'Configure',
                 'DetectorType',
                 'DetectorTypeAuto',
                 'NumberOfSweeps',
                 'SweepModeContinuous',
                 'VerticalScale']
class DriverOperation(FieldsClass):
    _pickup = ['Cache',
                 'ClearInterchangeWarnings',
                 'DriverSetup',
                 'GetNextCoercionRecord',
                 'GetNextInterchangeWarning',
                 'InterchangeCheck',
                 'InvalidateAllAttributes',
                 'IoResourceDescriptor',
                 'LogicalName',
                 'QueryInstrumentStatus',
                 'RangeCheck',
                 'RecordCoercions',
                 'ResetInterchangeCheck',
                 'Simulate']

class Display(FieldsClass):
    _pickup = ['NumberOfDivisions',
               'UnitsPerDivision']

class ExternalMixer(FieldsClass):
    _pickup = ['AverageConversionLoss',
                 'Bias',
                 'Configure',
                 'ConversionLossTable',
                 'Enabled',
                 'Harmonic',
                 'NumberOfPorts']

class Frequency(FieldsClass):
    _pickup = ['ConfigureCenterSpan',
                 'ConfigureStartStop',
                 'Offset',
                 'Start',
                 'Stop']

class Identity(FieldsClass):
    _pickup = ['Description',
             'GroupCapabilities',
             'Identifier',
             'InstrumentFirmwareRevision',
             'InstrumentManufacturer',
             'InstrumentModel',
             'Revision',
             'SpecificationMajorVersion',
             'SpecificationMinorVersion',
             'SupportedInstrumentModels',
             'Vendor']
    
class Level(FieldsClass):
    _pickup = ['AmplitudeUnits',
                 'Attenuation',
                 'AttenuationAuto',
                 'Configure',
                 'InputImpedance',
                 'Reference',
                 'ReferenceOffset']

class Marker(FieldsClass):
    _pickup = ['ActiveMarker',
                 'Amplitude',
                 'ConfigureEnabled',
                 'ConfigureSearch',
                 'Count',
                 'DisableAll',
                 'Enabled',
                 'FrequencyCounter',
                 'MakeDelta',
                 'Name',
                 'PeakExcursion',
                 'Position',
                 'Query',
                 'QueryReference',
                 'ReferenceAmplitude',
                 'ReferencePosition',
                 'Search',
                 'SetInstrumentFromMarker',
                 'SignalTrackEnabled',
                 'Threshold',
                 'Trace',
                 'Type']

class Preselector(FieldsClass):
    _pickup = ["Peak"]

class SweepCoupling(FieldsClass):
    _pickup = ['Configure',
                 'ResolutionBandwidth',
                 'ResolutionBandwidthAuto',
                 'SweepTime',
                 'SweepTimeAuto',
                 'VideoBandwidth',
                 'VideoBandwidthAuto']

class Trigger(FieldsClass):
    _pickup = ['External',
               'Source',
               'Video']

class Trace(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.session = parent.session.Traces[name]
        
        pick_from_session(self, [#'FetchY',
                                 #'ReadY',
                                 'Size',
                                 'Type'])
    def fetch_y(self):
        return array(list(self.session.FetchY()))
        
    def read_y(self, timeout_ms=10000):
        return array(list(self.session.ReadY(timeout_ms)))
    
    
class TraceContainer(OrderedDict):
    pass

class ShortCutSpecAn(ShortCut):
    _acquisition_fields = [("detector_type", "detector_type"),
               ("number_of_sweeps","number_of_sweeps")]
    
    _trace_related_fields = [("tr_size", "size"),
                               ("tr_type", "type")]
    _sweep_coupling_fields = [("resolution_bandwidth", "resolution_bandwidth")]    
    def __init__(self, parent):
        super(ShortCutSpecAn, self).__init__(parent)
        self.trace_idx = 1
        
    @property
    def trace_name(self):
        return self.parent.traces.keys()[self.trace_idx-1]

    @property
    def active_trace(self):
        return self.parent.traces[self.trace_name]
    
    def fetch(self):
        y_trace = self.parent.traces[self.trace_name].fetch_y()
        x_start = self.parent.frequency.start
        x_stop = self.parent.frequency.stop
        size = self.parent.traces[self.trace_name].size
        x_trace = linspace(x_start, x_stop, size, False)
        return x_trace, y_trace
    
add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._sweep_coupling_fields,
              'sweep_coupling')
add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._acquisition_fields,
              'acquisition')
add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._trace_related_fields,
              'sc_active_trace')


add_sc_fields_enum(ShortCutSpecAn, 'detector_type', '',
                                                    'auto_peak',
                                                    'average',
                                                    'max_peak',
                                                    'min_peak',
                                                    'sample',
                                                    'rms')
add_sc_fields_enum(ShortCutSpecAn, 'tr_type', '', 
                                              'clear_write',
                                              'max_hold',
                                              'min_hold',
                                              'video_average',
                                              'view',
                                              'store')             
                                

@register_wrapper('IVI-COM', 'IviSpecAn')
class IviComSpecAn(IviComWrapper):
    trace_cls = Trace
    def __init__(self, *args, **kwds):
        super(IviComSpecAn, self).__init__(*args, **kwds)
        self.acquisition = Acquisition(self.session.Acquisition, self)
        self.display = Display(self.session.Display, self)
        self.driver_operation = DriverOperation(self.session.DriverOperation, self)
        self.external_mixer = ExternalMixer(self.session.ExternalMixer, self)
        self.frequency = Frequency(self.session.Frequency, self)
        self.identity = Identity(self.session.Identity, self)
        self.level = Level(self.session.Level, self)
        self.marker = Marker(self.session.Marker, self)
        self.preselector = Preselector(self.session.Preselector, self)
        self.sweep_coupling = SweepCoupling(self.session.SweepCoupling, self)
        self.trigger = Trigger(self.session.Trigger, self)
        
        self.traces = TraceContainer()
        for trace_index in range(1, self.session.Traces.Count+1):
            name = self.session.Traces.Name(trace_index)
            self.traces[name] = self.trace_cls(name, self)
        self.traces.math = self.session.Traces.Math
        
        self.sc = ShortCutSpecAn(self)
        
    @property
    def sc_active_trace(self):
        return self.traces[self.sc.trace_name]