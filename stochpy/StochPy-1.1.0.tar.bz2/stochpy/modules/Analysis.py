#! /usr/bin/env python
"""
Analysis
========

This module provides functions for Stochastic Simulation Algorithms Analysis (SSA). Implemented SSAs import this module to perform their analysis. Plotting of time series species, propensities), distributions (species, propensities, distributions), autocorrelations, and autocovariances (species, propensities) is possible.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: May 17, 2013
"""

try:    
    import matplotlib.pyplot as plt  
    import matplotlib.colors as clr
    IS_PLOTTING = True
except: 
    IS_PLOTTING = False
    print "Matplotlib module is not available, thus it is impossible to create plots"

try: 
    import numpy as np
except:
    print "Error: NumPy module is not available. "
    sys.exit()

import copy,sys

def getDataForTimeSimPlot(Arr_data,n_points2plot = 10000):
    """
    getDataForTimeSimPlot(data,n_points2plot = 10000)
    
    Input:
     - *Arr_data* (numpy array)
     - *n_points2plot* [default = 10000] (integer)
    """    
    len_data = len(Arr_data)    
    if (len_data > 100000): # use n_points2plot only if datasets become too large     
        L_data2plot = [Arr_data[0]]
        step_size = len_data/int(abs(n_points2plot))        
        for i in xrange(step_size,len_data,step_size):
            t = Arr_data[i][0]            
            data_point = copy.deepcopy(list(L_data2plot[-1][1:]))
            data_point.insert(0,t)
            L_data2plot.append(data_point)
            L_data2plot.append(Arr_data[i])
        print "Info: Plotting %s out of %s points.\nUse the argument 'n_points2plot' to alter the number of plotted events.\nUse n_points2plot='All' to plot all the data points."  % (n_points2plot,len_data)
    else: 
        L_data2plot = copy.deepcopy(list(Arr_data))
        j=1       
        for i in xrange(1,len_data):
            t = Arr_data[i][0]
            data_prev = copy.deepcopy(Arr_data[i-1]) # data of previous ...
            data_prev[0] = t
            L_data2plot.insert(j,data_prev)
            j+=2              
    return np.array(L_data2plot)

def Count(L_data,L_edges):
    """
    Count(L_data,L_edges)
    
    Input:
     - *L_data* (list)
     - *L_edges* (list)
    """
    n_edges = len(L_edges)
    L_output = np.zeros(n_edges)
    for value in L_data:    
        for i in xrange(n_edges-1):
            if (value >= L_edges[i]) and (value < L_edges[i+1]):
                L_output[i]+=1  
    return np.array(L_output)  
    
def GetDataDistributions(L_sim_output,L_names):  
    """
    Get distributions, means, standard deviations, and the (raw) moments
      
    Input:
    - *L_sim_output* (list)
    - *L_names* (list)
    """     
    n_names = len(L_names)
    L_distributions = [{} for i in xrange(n_names)]
    endtime = L_sim_output[-1][0]
    for timestep in xrange(len(L_sim_output)-1):
        for i in xrange(n_names): 
            try:
                L_distributions[i][L_sim_output[timestep][i+1]] += L_sim_output[timestep+1][0] - L_sim_output[timestep][0]
            except KeyError:
                L_distributions[i][L_sim_output[timestep][i+1]] = L_sim_output[timestep+1][0] - L_sim_output[timestep][0]  
    
    L_probability_mass = []
    D_means = {}
    D_stds = {}
    D_moments = {}
    for i in xrange(n_names):
        L_x_i = np.array(sorted(L_distributions[i]))     
        L_y_i = np.array([L_distributions[i][x_i] for x_i in sorted(L_distributions[i])])/float(endtime) # probability = dt/T
        mean = (L_x_i*L_y_i).sum()
        mean_sq = (L_x_i**2*L_y_i).sum()
        var = mean_sq - mean*mean
        std = var**0.5
        L_probability_mass.append([L_x_i,L_y_i])
        id_name = L_names[i]
         
        D_means[id_name] = mean
        D_stds[id_name] = std
          
        D_moments[id_name] = {}
        D_moments[id_name]['1'] = mean 
        D_moments[id_name]['2'] = mean_sq
        D_moments[id_name]['3'] = (L_x_i**3*L_y_i).sum()
        D_moments[id_name]['4'] = (L_x_i**4*L_y_i).sum()        
    del L_sim_output,L_distributions
    return (L_probability_mass,D_means,D_stds,D_moments)        
    
def Binning(x,y,bin_size):
    """
    Binning(x,y,bin_size)
    
    Binning of the PDF
    
    bin_size is the number of indices for binning (23/01/2013)   
    
    Input:
     - *x* list of x-values
     - *y* list of probabilities for each x[i]
     - *bin_size* (integer)     
    """   
    L_binned_data = []
    nprobabilities = len(x)
    if type(bin_size) == int:
         pass
    elif type(bin_size) == float:
         print "Warning: The 'bin_size' must an integer rather than a float; float %s is rounded to %s" % (bin_size,int(bin_size))
         bin_size = int(bin_size)
    else:
        print "Error: The 'bin_size' must be an integer"
        sys.exit()
    if (nprobabilities > 1) and (type(bin_size) == int):        # binning is possible    
        xdif = x[1]-x[0]
        if (bin_size <= 1) or (bin_size > nprobabilities):      # no binning because of the bin size
            data = np.array([x,y]).transpose()            
            data[:,0] += xdif/2.0                               # probability must be around the x value
        elif (bin_size > 1):                                    # do binning            
            max_index = y.index(max(y))                         # maximum prob index
            ### Get interval around the maximum value ###
            L_interval = range(int(max_index-(bin_size/2.0)+1),max_index+int(round(bin_size/2.0)+1)) # Get interval around maximum prob
            if (bin_size%2):
                L_interval.pop()
            index_lb = L_interval[0]            
            while index_lb < 0:                                 # index lb smaller than zero
                L_interval.remove(index_lb)                     
                L_interval.append(L_interval[-1]+1)
                index_lb = min(L_interval) 
            while L_interval[-1] > (nprobabilities-1):          # index ub larger than maximum index
                L_interval.pop()
                L_interval.insert(0,L_interval[0]-1)
            #############################################   
            L_binned_data.append([x[L_interval[-1]]+xdif/2.0 ,sum(y[L_interval[0]:L_interval[-1]+1])/float(bin_size)])           
            L_individuals = []                                  # locations with bin_size = 1
            if L_interval[0]:
                nbins1 = (L_interval[0]-1)/bin_size             # nbins before L_interval around max prob
                start1 = L_interval[0]-1 - nbins1*bin_size      # start location of binning before interval
                if L_interval[0] == 1:
                    L_individuals.append(0)
            else:                                               # interval around max goes until the first species amount
                L_binned_data.append([x[L_interval[0]]+xdif/2.0 ,sum(y[L_interval[0]:L_interval[-1]+1])/float(bin_size)]) 
                nbins1 = 0
                start1 = 0
                L_individuals.append(0)
            start2 = L_interval[-1]                             # start location of binning after interval
            nbins2 = (nprobabilities-1 - start2)/bin_size       # nbins after interval around max prob
            L_individuals += [i for i in xrange(0,start1)]        
            L_individuals += [i for i in xrange(start2+1+(bin_size*nbins2),nprobabilities)]
            x_ = np.array(x)
            y_ = np.array(y)
            for i in xrange(nbins1):            
                L_binned_data.append([x_[start1+bin_size]+xdif/2.0 ,sum(y_[start1:start1+bin_size])/float(bin_size)])
                start1+=bin_size
            for i in xrange(nbins2):  
                L_binned_data.append([x[start2+bin_size]+xdif/2.0 ,sum(y[start2:start2+bin_size])/float(bin_size)]) 
                start2+=bin_size                  
            for i in L_individuals:
                L_binned_data.append([x[i],y[i]])
            data = np.array(sorted(L_binned_data))     
    else:                                                       # binning is not possible
        data = np.array([x,y]).transpose()    
    return data

def LogBin(L_data,factor):  
    """
    LogBin(data,factor)
    
    Function that creates log bins  

    Input: 
     - *L_data* (list)
     - *factor* (float) determines the width of the bins
    Output: 
     - *L_x* (list)
     - *L_y* (list)
     - *nbins* (integer)
    """
    xmin = float(min(L_data))    
    nbins = int(np.ceil(np.log(max(L_data)/xmin)/np.log(factor)))  
    L_edges = np.zeros(nbins)
    L_edges[0] = xmin     
    for i in xrange(1,nbins):
        L_edges[i] = L_edges[i-1]*factor  
    L_x  = L_edges[0:(nbins-1)]+np.diff(L_edges)/2  
    L_dp = Count(L_data,L_edges)
    L_ry = np.array(L_dp[0:(nbins-1)])  
    L_dedges = np.array(np.diff(L_edges))  
    L_y = L_ry/(sum(L_ry)*L_dedges) 
    return(L_x,L_y,nbins)

def ObtainWaitingtimes(data_stochsim,L_reactions): 
    """    
    ObtainWaitingtimes(data_stochsim,L_reactions)
    
    This function extracts the waiting times for each reaction of the model from the used SSA output.

    Input:
     - *data_stochsim* (python data object) that stores all simulation data
     - *L_reactions* (list)
    output:
     - *D_waiting_times* (dict) 
  
    Note: It is impossible to use this function in combination with the Tau-leaping method, because the Tau-Leaping results are not exact!
    """
    L_time = data_stochsim.time.flatten()
    L_fired_reactions = data_stochsim.fired_reactions              # Reactions that fired at some time point
    D_waiting_times = {}
    D_last_time_fired = {}
    nreactions = len(L_reactions)
    for r_id in L_reactions:     
        D_waiting_times[r_id] = []                                 # create a list that will contain event waiting times for reaction r
        
    ### np.nan (e.g. events) is ignored, because we determine it only for fired reactions like (1,2,3, .... nreactions)
    for (current_time,r_index) in zip(L_time[1:],L_fired_reactions): # fixed January 21 2013        
        for i in xrange(1,nreactions+1):                           # fired reactions are (1,2,3, .... nreactions)
            if r_index == i:
                if r_index in D_last_time_fired:
                    D_last_time_fired[r_index]                     # A previous firing time is necessary                                  
                    D_waiting_times[L_reactions[int(r_index-1)]].append(current_time-D_last_time_fired[r_index]) # Add inter-arrival time
                    D_last_time_fired[r_index] = current_time      # Update last firing time     
                else:
                    D_last_time_fired[r_index] = current_time      # Initial firing time
    return D_waiting_times

def GetAverageResults(L_regular_grid):
    """
    GetAverageResults(L_regular_grid)
    
    Gets the averaged output of multiple trajectories

    Input: 
     - *L_regular_grid* (nested list)
    """
    L_means = []
    L_stds = []
    for L_data in L_regular_grid:
        L_means.append(np.mean(L_data,0))
        L_stds.append(np.std(L_data,0))    
    return (L_means,L_stds)
    
def RemoveBias(x, axis):
    "Subtracts an estimate of the mean from signal x at axis"
    padded_slice = [slice(d) for d in x.shape]
    padded_slice[axis] = np.newaxis
    mn = np.mean(x, axis=axis)
    return x - mn[tuple(padded_slice)]        

def AutoCov(s, **kwargs):
    """Returns the autocovariance of signal s at all lags.

    Notes
    -----
    
    Adheres to the definition
    sxx[k] = E{S[n]S[n+k]} = cov{S[n],S[n+k]}
    where E{} is the expectation operator, and S is a zero mean process
    """
    # only remove the mean once, if needed
    debias = kwargs.pop('debias', True)
    axis = kwargs.get('axis', -1)
    if debias:
        s = RemoveBias(s, axis)
    kwargs['debias'] = False
    return CrossCov(s, s, **kwargs)   
    
def FFTconvolve(in1, in2, mode="full", axis=None):
    """
    Convolve two N-dimensional arrays using FFT. See convolve.
    """
    s1 = np.array(in1.shape)
    s2 = np.array(in2.shape)
    complex_result = (np.issubdtype(in1.dtype, np.complex) or
                      np.issubdtype(in2.dtype, np.complex))
    if axis is None:
        size = s1+s2-1
        fslice = tuple([slice(0, int(sz)) for sz in size])
    else:
        equal_shapes = s1==s2
        # allow equal_shapes[axis] to be False
        equal_shapes[axis] = True
        assert equal_shapes.all(), 'Shape mismatch on non-convolving axes'
        size = s1[axis]+s2[axis]-1
        fslice = [slice(l) for l in s1]
        fslice[axis] = slice(0, int(size))
        fslice = tuple(fslice)

    # Always use 2**n-sized FFT
    fsize = int(2**np.ceil(np.log2(size)))
    if axis is None:
        IN1 = np.fft.fftpack.fftn(in1,fsize)
        IN1 *= np.fft.fftpack.fftn(in2,fsize)
        ret = np.fft.fftpack.ifftn(IN1)[fslice].copy()
    else:
        IN1 = np.fft.fftpack.fft(in1,fsize,axis=axis)
        IN1 *= np.fft.fftpack.fft(in2,fsize,axis=axis)
        ret = np.fft.fftpack.ifft(IN1,axis=axis)[fslice].copy()
    del IN1
    if not complex_result:
        ret = ret.real
    if mode == "full":
        return ret
    elif mode == "same":
        if np.product(s1,axis=0) > np.product(s2,axis=0):
            osize = s1
        else:
            osize = s2
        return _centered(ret,osize)
    elif mode == "valid":
        return _centered(ret,abs(s2-s1)+1)   


def CrossCov(x, y, axis=-1, all_lags=False, debias=True):
    """Returns the crosscovariance sequence between two ndarrays.
    This is performed by calling fftconvolve on x, y[::-1]

    Parameters
    ----------

    x: ndarray
    y: ndarray
    axis: time axis
    all_lags: {True/False}
       whether to return all nonzero lags, or to clip the length of s_xy
       to be the length of x and y. If False, then the zero lag covariance
       is at index 0. Otherwise, it is found at (len(x) + len(y) - 1)/2
    debias: {True/False}
       Always removes an estimate of the mean along the axis, unless
       told not to.

    Notes
    -----

    cross covariance is defined as
    sxy[k] := E{X[t]*Y[t+k]}, where X,Y are zero mean random processes
    """
    if x.shape[axis] != y.shape[axis]:
        raise ValueError('CrossCov() only works on same-length sequences for now')
    if debias:
        x = RemoveBias(x, axis)
        y = RemoveBias(y, axis)
    slicing = [slice(d) for d in x.shape]
    slicing[axis] = slice(None,None,-1)
    sxy = FFTconvolve(x, y[tuple(slicing)], axis=axis, mode='full')
    N = x.shape[axis]
    sxy /= N
    if all_lags:
        return sxy
    slicing[axis] = slice(N-1,2*N-1)
    return sxy[tuple(slicing)]
        
def Autocorrelation(s, **kwargs):
    """
    Returns the autocorrelation of signal s at all lags.

    Notes
    -----
    
    Adheres to the definition
    rxx[k] = E{S[n]S[n+k]}/E{S*S} = cov{S[n],S[n+k]}/sigma**2
    where E{} is the expectation operator, and S is a zero mean process
    """
    # only remove the mean once, if needed
    debias = kwargs.pop('debias', True)
    axis = kwargs.get('axis', -1)
    if debias:
        s = RemoveBias(s, axis)
        kwargs['debias'] = False
    sxx = AutoCov(s, **kwargs)
    all_lags = kwargs.get('all_lags', False)
    if all_lags:
        i = (2*s.shape[axis]-1)/2
        sxx_0 = sxx[i]
    else:
        sxx_0 = sxx[0] 
    if not sxx_0:
        sxx = [np.nan for i in xrange(len(sxx))] # Modification
    else:    
        sxx /= sxx_0
    #print sxx_0    
    return sxx

class DoPlotting():
  """
  This class initiates the plotting options.

  Input: 
   - *species_labels* (list) [S1,S2, ..., Sn]
   - *rate_labels* (list) [R1, R2, ..., Rm] 
  """
  def __init__(self,species_labels,rate_labels,plotnum=1):
      self.species_labels = species_labels
      self.rate_labels = rate_labels
      self.number_of_rates = len(rate_labels)
      self.plotnum  = plotnum      
      # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/colors.py
      self.colors = ['#0000FF','#00CC00','#FF0033','#FF00CC','#6600FF','#FFFF00','#000000','#CCCCCC','#00CCFF','#99CC33','#FF6666','#FF99CC','#CC6600','#003300','#CCFFFF','#9900FF','#CC6633','#FFD700','#C0C0C0']
      
    
  def ResetPlotnum(self):
      """ Reset figure numbers if trajectories > 1 """
      self.plotnum = 1 
      
  def TimeSeries(self,data,n_points2plot,datatype2plot,L_labels,trajectory_index,linestyle,marker,colors,title,xlabel,ylabel,IsLegend):      
      """
      TimeSeries(data,n_points2plot,datatype2plot,trajectory_index,linestyle,marker,colors,title)
      
      Tracks the propensities and/or species over time

      Input: 
       - *data* (array)
       - *n_points2plot* (integer)
       - *datatype2plot* (list)
       - *L_labels* (list)
       - *trajectory_index* (integer)
       - *linestyle* (string)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)
       - *IsLegend* (boolean)
      """
      plt.figure(self.plotnum)      
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot]      
      L_data = getDataForTimeSimPlot(data,n_points2plot)
      L_time = L_data[:,0]   
      if len(datatype2plot) == 1:
          j = trajectory_index
      else:
          j=0

      for i in datatype2plot_indices:
          y = L_data[:,i+1]          
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0

          if colors == None:
              plt.plot(L_time,y,marker,ls = linestyle,color = self.colors[j])
          else:
              if clr.is_color_like(colors[j]):
                  plt.plot(L_time,y,marker,ls = linestyle,color = colors[j])
              else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.plot(L_time,y,marker,ls = linestyle,color = self.colors[j])
                  colors = None
          j+=1
      if IsLegend:
          plt.legend(datatype2plot,numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel(xlabel) 
      plt.ylabel(ylabel)      
      
  def Autocorrelations(self,lags,data,datatype2plot,L_labels,trajectory_index,linestyle,marker,colors,title,xlabel,ylabel,IsLegend):      
      """
      Autocorrelations(data,species2plot,trajectory_index,linestyle,marker,colors,title)

      Input:
       - *data* (array)      
       - *datatype2plot* (list) 
       - *L_labels* (list)
       - *trajectory_index* (integer)       
       - *linestyle* (string)
       - *marker* string)
       - *colors* (list)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)
       - *IsLegend* (boolean)
      """
      plt.figure(self.plotnum)
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot]
      if len(datatype2plot) == 1:
          j = trajectory_index
      else:
          j=0          
      
      for i in datatype2plot_indices:         
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0
                                  
          y = data[i][0:len(lags)]          
          if colors == None:
              plt.plot(lags,y,marker,ls = linestyle,color = self.colors[j])
          else:   
              if clr.is_color_like(colors[j]):             
                  plt.plot(lags,y,marker,ls = linestyle,color = colors[j])
              else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.plot(lags,y,marker,ls = linestyle,color = self.colors[j]) 
                  colors = None
          j+=1 
      if IsLegend:    
          plt.legend(datatype2plot,numpoints=1,frameon=True)      
      plt.title(title)
      plt.xlabel(xlabel) 
      plt.ylabel(ylabel)
      
  def Distributions(self,distributions,datatype2plot,L_labels,trajectory_index,linestyle,linewidth,colors,title,xlabel,ylabel,IsLegend,bin_size):    
      """
      Distributions(distributions,datatype2plot,trajectory_index,linestyle,colors,title,bin_size)
      
      Plots the distributions of species and/or propensities

      Input:
       - *distributions* (nested list)
       - *datatype2plot* (list)
       - *L_labels* (list)
       - *trajectory_index* (integer)
       - *colors* (list)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)       
       - *IsLegend* (boolean)
       - *bin_size* (string)
      """ 
      plt.figure(self.plotnum)
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot]     
      if len(datatype2plot) == 1:
          j = trajectory_index
      else:
          j=0

      for i in datatype2plot_indices: 
          x = list(copy.copy(distributions[i][0]))
          y = list(copy.copy(distributions[i][1]))          
          L_data = Binning(x,y,bin_size)
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0
          if colors == None:
              plt.step(L_data[:,0],L_data[:,1],ls = linestyle,lw = linewidth,color = self.colors[j])	# Plot
          else:
             if clr.is_color_like(colors[j]):             
                  plt.step(L_data[:,0],L_data[:,1],ls = linestyle,lw = linewidth,color = colors[j])     
             else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.step(L_data[:,0],L_data[:,1],ls = linestyle,lw = linewidth,color = self.colors[j])
                  colors = None
          j+=1
      if IsLegend:
          plt.legend(datatype2plot,numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)            

  def WaitingtimesDistributions(self,D_waiting_times,rates2plot,trajectory_index,linestyle,marker,colors,title,xlabel,ylabel,IsLegend):
      """
      WaitingtimesDistributions(D_waiting_times,rates2plot,trajectory_index,linestyle,marker,colors,title)
      
      Plots the waiting times for each reaction in the model. Makes use of ObtainWaitingtimes to derive the waiting times out of the SSA output.
 
      Input: 
       - *D_waiting_times* (dict)
       - *rates2plot* (list)
       - *trajectory_index* (integer)
       - *linestyle* (string)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)
       - *IsLegend* (boolean)
      """
      plt.figure(self.plotnum)               
      if len(rates2plot) == 1:
          j = trajectory_index
      else:
          j=0

      L_legend_names = []
      for r_id in rates2plot:                        
          L_waiting_times = D_waiting_times[r_id]       # get list of waiting times for a given reaction
          if len(L_waiting_times) > 1:			# At least 2 waiting times are necessary per reaction
              (x,y,nbins) = LogBin(L_waiting_times,1.5) # Create logarithmic bins (HARDCODED 1.5)
              if colors == None:              
                  if j >= len(self.colors):                  
                      j=0
              elif colors:
                  if j >= len(colors):
                      j=0                 
              if colors == None:
                  plt.loglog(x,y,marker,ls = linestyle,color = self.colors[j])
              else:
                  if clr.is_color_like(colors[j]):           
                      plt.loglog(x,y,marker,ls = linestyle,color = colors[j])
                  else:
                      print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                      plt.loglog(x,y,marker,ls = linestyle,color = self.colors[j])
                      colors = None                            
              L_legend_names.append(r_id)
              j+=1
      plt.title(title)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)
      if IsLegend:
          plt.legend(L_legend_names,numpoints=1,frameon=True)
      
  def AverageTimeSeries(self,L_means,L_stds,L_time,nstd,datatype2plot,L_labels,linestyle,marker_,colors,title,xlabel,ylabel,IsLegend):
      """
      AverageSpeciesTimeSeries(L_means,L_stds,L_time,datatype2plot,linestyle,marker_,colors,title)
      
      Plots the average and standard deviation of datatype on a regular grid

      Input:
       - *L_means* (nested list)
       - *L_stds* (nested list)
       - *L_time* (list)
       - *nstd* (float)
       - *datatype2plot* (list)
       - *L_labels* (list)
       - *L_time* (list)
       - *linestyle* (string)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)
       - *IsLegend* (boolean)
      """ 
      assert nstd > 0, "Error: The number of STDs must be a value larger than zero"
      plt.figure(self.plotnum)
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot] 
      j=0
      for i in datatype2plot_indices:
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0
          npoints = len(L_time)
          if colors == None:
              plt.errorbar(L_time,L_means[i][0:npoints],yerr = nstd*np.array(L_stds[i][0:npoints]),color = self.colors[j],ls = linestyle,marker = marker_,label = L_labels[i]) # plot with y-axis error bars
          else:
              if clr.is_color_like(colors[j]):     
                  plt.errorbar(L_time,L_means[i][0:npoints],yerr = nstd*np.array(L_stds[i][0:npoints]),color = colors[j],ls = linestyle,marker = marker_,label = L_labels[i])
              else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.errorbar(L_time,L_means[i][0:npoints],yerr = nstd*np.array(L_stds[i][0:npoints]),color = self.colors[j],ls = linestyle,marker = marker_,label = L_labels[i])
                  colors = None
          j+=1
      if IsLegend:
          plt.legend(numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)

  def AverageDistributions(self,L_means,L_stds,nstd,datatype2plot,L_labels,linestyle,marker_,colors,title,xlabel,ylabel,IsLegend):
      """      
      Plots the average and standard deviation

      Input:
       - *L_means* (nested list)
       - *L_stds* (nested list)
       - *nstd* (float)
       - *L_labels* (list)
       - *linestyle* (string)
       - *title* (string)
       - *xlabel* (string)
       - *ylabel* (string)
       - *IsLegend* (boolean)
      """
      assert nstd > 0, "Error: The number of STDs must be a value larger than zero"     
      plt.figure(self.plotnum)
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot]     
      j=0
      for i in datatype2plot_indices:
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0 
          if colors == None:              
              plt.errorbar(L_means[i][0],L_means[i][1],yerr = nstd * np.array(L_stds[i][1]),color = self.colors[j],ls = linestyle,marker = marker_,label = L_labels[i]) # plot with y-axis error bars
          else:
              if clr.is_color_like(colors[j]):     
                  plt.errorbar(L_means[i][0],L_means[i][1],yerr = nstd*np.array(L_stds[i][1]),color = colors[j],ls = linestyle,marker = marker_,label = L_labels[i])
              else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.errorbar(L_means[i][0],L_means[i][1],yerr = nstd * np.array(L_stds[i][1]),color = self.colors[j],ls = linestyle,marker = marker_,label = L_labels[i])
                  colors = None                  
          j+=1
      if IsLegend:
          plt.legend(numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)
      
  def AverageDistributionsCI(self,L_means,L_stds,nstd,datatype2plot,L_labels,colors,title,xlabel,ylabel,IsLegend):
      assert nstd > 0, "Error: The number of STDs must be a value larger than zero"      
      plt.figure(self.plotnum)
      datatype2plot_indices = [L_labels.index(datatype) for datatype in datatype2plot]           
      for i in datatype2plot_indices:   
          L_s_amount = copy.copy(L_means[i][0])
          L_mu =  copy.copy(L_means[i][1])
          L_sigma =  copy.copy(L_stds[i][1])

          # Add an additional value
          L_s_amount.append(L_s_amount[-1]+1)
          L_mu.append(L_mu[-1])
          L_sigma.append(L_sigma[-1])

          X_i = []
          Y_i = []
          L_errors = []
          for j in xrange(len(L_s_amount)):
              if (not L_s_amount[j] == L_s_amount[0]) and (not L_s_amount[j] == L_s_amount[-1]):
                  X_i.append(L_s_amount[j])
                  Y_i.append(L_mu[j-1])
                  L_errors.append(L_sigma[j-1])
              X_i.append(L_s_amount[j])
              Y_i.append(L_mu[j])
              L_errors.append(L_sigma[j])
          X_e = np.concatenate([X_i, X_i[::-1]])
          Y_e = np.concatenate([np.array(Y_i) - nstd*np.array(L_errors) ,(np.array(Y_i) + nstd*np.array(L_errors))[::-1]])   
      
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0
          elif colors:
              if j >= len(colors):
                  j=0 
          if colors == None:                         
              plt.fill(X_e-0.5,Y_e,  alpha=.25, ec='None', label='%s STD confidence interval' % nstd,color = self.colors[j]) 
              plt.plot(np.array(X_i)-0.5,np.array(Y_i),color = self.colors[j])
          else:
              if clr.is_color_like(colors[j]):     
                  plt.fill(X_e-0.5,Y_e,  alpha=.25, ec='None', label='%s STD confidence interval' % nstd,color = colors[j]) 
                  plt.plot(np.array(X_i)-0.5,np.array(Y_i),color = colors[j])
              else:
                  print "Warning: '%s' is not recognized as a valid color code" % colors[j]
                  plt.fill(X_e-0.5,Y_e,  alpha=.25, ec='None', label='%s STD confidence interval' % nstd,color = self.colors[j]) 
                  plt.plot(np.array(X_i)-0.5,np.array(Y_i),color = self.colors[j])      
                  colors = None
      if IsLegend:
          plt.legend(numpoints=1,frameon=True)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)
      plt.title(title)
          
