from pyivi.ivifactory import register_wrapper
from pyivi.ivicom import IviComWrapper
from pyivi.ivicom.ivicomwrapper import FieldsClass, \
                                       pick_from_session
from pyivi.common import add_sc_fields_enum, \
                         ShortCut, \
                         add_sc_fields

from numpy import array
from collections import OrderedDict

class Measurement(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.session = parent.session.Measurements[name]
        
        pick_from_session(self,['Create',
                                'DataToMemory',
                                'Delete',
                                'Format',
                                'GetSParameter',
                                'Limit',
                                'Markers',
                                'QueryStatistics',
                                'SetSParameter',
                                'Smoothing',
                                'SmoothingAperture',
                                'Trace',
                                'TraceMath'])
    
    def fetch_complex(self):
        real_, imag_ = self.session.FetchComplex()
        return array(list(real_)) + 1j*array(list(imag_))
    
    def fetch_memory_complex(self):
        real_, imag_ = self.session.FetchMemoryComplex()
        return array(list(real_)) + 1j*array(list(imag_))
    
    def fetch_x(self):
        return array(list(self.session.FetchX()))
    
    def fetch_memory_formatted(self):
        return array(list(self.session.FetchMemoryFormatted()))

class ShortCutNA(ShortCut):
    
    _channel_related_fields = [("if_bandwidth", "if_bandwidth"),
                               ("averaging", "averaging"),
                               ("averaging_factor", "averaging_factor"),
                               ("sweep_time", "sweep_time"),
                               ("sweep_type", "sweep_type")]
    
    _measurement_related_fields = [("if_bandwidth", "if_bandwidth"),
                               ("averaging", "averaging"),
                               ("averaging_factor", "averaging_factor"),
                               ("sweep_time", "sweep_time"),
                               ("sweep_type", "sweep_type")]
    
    _sweep_coupling_fields = [("resolution_bandwidth", "resolution_bandwidth")]    
    def __init__(self, parent):
        super(ShortCutNA, self).__init__(parent)
        self.channel_idx = 1
        self.measurement_idx = 1
    
    @property
    def input_port(self):
       return self.active_measurement.get_s_parameter()[0]
   
    @input_port.setter
    def input_port(self, val):
        self.active_measurement.set_s_parameter(val,
                                        self.output_port)
        return val
    
    @property
    def output_port(self):
        return self.active_measurement.get_s_parameter()[1]
    
    @output_port.setter
    def output_port(self, val):
        self.active_measurement.set_s_parameter(
                                        self.input_port,
                                        val)
    
    @property
    def measurement_name(self):
        return self.active_channel.measurements.keys()[self.measurement_idx-1]
    
    @property
    def active_measurement(self):
        return self.active_channel.measurements[self.measurement_name]
    
    def clear_average(self):
        self.active_channel.clear_average()
        
    @property
    def channel_name(self):
        return self.parent.channels.keys()[self.channel_idx-1]

    @property
    def active_channel(self):
        return self.parent.channels[self.channel_name]
    
    def create_measurement(self, input_port=2, output_port=1):
        self.active_measurement.create(input_port, output_port)
    
    def fetch(self):
        y_trace = self.parent.traces[self.trace_name].fetch_y()
        x_start = self.parent.frequency.start
        x_stop = self.parent.frequency.stop
        size = self.parent.traces[self.trace_name].size
        x_trace = linspace(x_start, x_stop, size, False)
        return x_trace, y_trace
    
    
    
add_sc_fields(ShortCutNA, 
              ShortCutNA._channel_related_fields, 
              'sc_active_channel')


class Channel(object):
    measurement_cls = Measurement
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.session = parent.session.Channels[name]
        
        pick_from_session(self, ['AsynchronousTriggerSweep',
                                 'Averaging',
                                 'AveragingFactor',
                                 'CWFrequency',
                                 'ClearAverage',
                                 'Correction',
                                 'GetCorrectionArrays',
                                 'IFBandwidth',
                                 'Number',
                                 'Points',
                                 'PortExtension',
                                 'PortExtensionStatus',
                                 'Segment',
                                 'SetCorrectionArrays',
                                 'SourcePower',
                                 'StimulusRange',
                                 'SweepMode',
                                 'SweepTime',
                                 'SweepTimeAuto',
                                 'SweepType',
                                 'TriggerMode',
                                 'TriggerSweep'])
        self.measurements = OrderedDict()
        for meas_index in range(1, self.session.Measurements.Count+1):
            name = self.session.Measurements.Name(meas_index)
            self.measurements[name] = self.measurement_cls(name, self)

@register_wrapper('IVI-COM', 'AgNA')
class AgNA(IviComWrapper):
    _repeated_capabilities = {}
    channel_cls = Channel
    def __init__(self, *args, **kwds):
        super(AgNA, self).__init__(*args, **kwds)
        self.channels = OrderedDict()
        for channel_index in range(1, self.session.Channels.Count+1):
            name = self.session.Channels.Name(channel_index)
            self.channels[name] = self.channel_cls(name, self)
        self.sc = ShortCutNA(self)
        
    @property
    def sc_active_channel(self):
        return self.channels[self.sc.channel_name]