from pyivi.ivifactory import register_wrapper
from pyivi.ivic import IviCWrapper
from pyivi.ivic.ivicwrapper import RepeatedCapability, \
                                   add_repeated_capability
from pyivi.common import add_sc_fields_enum, \
                         ShortCut, \
                         add_sc_fields
from definesivispecan import add_props

import ctypes
from numpy import array, double, zeros, frombuffer, linspace

class ShortCutSpecAn(ShortCut):
    _acquisition_fields = [("detector_type", "detector_type"),
               ("number_of_sweeps","number_of_sweeps")]
    
    _trace_related_fields = [("tr_size", "trace_size"),
                               ("tr_type", "trace_type")]
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
        y_trace = self.parent.traces[self.trace_name].fetch_y_trace()
        x_start = self.parent.frequency_start
        x_stop = self.parent.frequency_stop
        size = self.parent.traces[self.trace_name].trace_size
        x_trace = linspace(x_start, x_stop, size, False)
        return x_trace, y_trace
    
    

add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._sweep_coupling_fields)
add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._acquisition_fields)
add_sc_fields(ShortCutSpecAn, 
              ShortCutSpecAn._trace_related_fields,
              'sc_active_trace')
add_sc_fields_enum(ShortCutSpecAn, 'tr_type', '', 
                                              'clear_write',
                                              'max_hold',
                                              'min_hold',
                                              'video_average',
                                              'view',
                                              'store')            
add_sc_fields_enum(ShortCutSpecAn, 'detector_type', '',
                                                    'auto_peak',
                                                    'average',
                                                    'max_peak',
                                                    'min_peak',
                                                    'sample',
                                                    'rms')
class TraceSpecAn(RepeatedCapability):
    def fetch_y_trace(self):
        return self.parent.fetch_y_trace(self.name)

    def read_y_trace(self, timeout_ms = 10000):
        return self.parent.read_y_trace(self.name, timeout_ms=timeout_ms)

@register_wrapper('IVI-C', 'IviSpecAn')
class IviCSpecAn(IviCWrapper):
    _repeated_capabilities = {}
    
    def __init__(self, *args, **kwds):
        super(IviCSpecAn, self).__init__(*args, **kwds)
        self.sc = ShortCutSpecAn(self)
    
    @property
    def sc_active_trace(self):
        return self.traces[self.sc.trace_name]
    
    def initiate_acquisition(self):
        self.call('InitiateAcquisition', self.visession)
    
    def fetch_y_trace(self, trace_name=None):
        """
        Same as fetch_waveform, but also initializes an acquisition
        """
        
        if not trace_name:
            trace_name = self.traces.keys()[0]
        trace_name_c = ctypes.c_char_p(trace_name)
        trace = self.traces[trace_name]
        py_len = trace.trace_size
        length = ctypes.c_int(py_len)
        arr = ctypes.c_double*py_len
        data = zeros(py_len, dtype = double)
        arr = arr.from_buffer_copy(data.data)
        actual_length = ctypes.c_int()
        initial_x = ctypes.c_double()
        x_increment = ctypes.c_double()
        self.call('FetchYTrace',
                  self.visession,
                  trace_name_c,
                  length,
                  ctypes.byref(actual_length),
                  arr)
        numpy_y = frombuffer(arr, dtype = double)
        return numpy_y
    
    
    def read_y_trace(self, trace_name=None, timeout_ms=10000):
        """
        Same as fetch_waveform, but also initializes an acquisition
        """
        
        if not trace_name:
            trace_name = self.traces.keys()[0]
        trace_name_c = ctypes.c_char_p(trace_name)
        trace = self.traces[trace_name]
        timeout_ms_c = ctypes.c_int32(timeout_ms)
        py_len = trace.trace_size
        length = ctypes.c_int(py_len)
        arr = ctypes.c_double*py_len
        data = zeros(py_len, dtype = double)
        arr = arr.from_buffer_copy(data.data)
        actual_length = ctypes.c_int()
        initial_x = ctypes.c_double()
        x_increment = ctypes.c_double()
        self.call('ReadYTrace',
                  self.visession,
                  trace_name_c,
                  timeout_ms_c,
                  length,
                  ctypes.byref(actual_length),
                  arr)
        numpy_y = frombuffer(arr, dtype = double)
        return numpy_y
    

        
add_repeated_capability(IviCSpecAn, 'Trace', TraceSpecAn)
add_props(IviCSpecAn)