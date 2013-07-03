from numpy import ma,array,linspace,log,cos,sin,pi,zeros,exp,arange
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.ticker import FixedLocator, AutoLocator, ScalarFormatter
import matplotlib.transforms as transforms
import matplotlib.axis as maxis
import matplotlib.artist as artist
from matplotlib.projections import register_projection
from matplotlib.pyplot import rcParams,figure

from thermodynamics import VirtualTemp,Latentc,SatVap,MixRatio


from UserDict import UserDict
from datetime import datetime
import os,sys

R = 287.05
Cp = 1004.

class SkewXTick(maxis.XTick):
    #Copyright (c) 2008 Ryan May
    def draw(self, renderer):
        if not self.get_visible(): return
        renderer.open_group(self.__name__)

        if self.gridOn:
            self.gridline.draw(renderer)
        if self.tick1On:
            self.tick1line.draw(renderer)
        if self.tick2On:
            self.tick2line.draw(renderer)

        if self.label1On:
            self.label1.draw(renderer)
        if self.label2On:
            self.label2.draw(renderer)

        renderer.close_group(self.__name__)

    def set_clip_path(self, clippath, transform=None):
        artist.Artist.set_clip_path(self, clippath, transform)
        self.tick1line.set_clip_path(clippath, transform)
        self.tick2line.set_clip_path(clippath, transform)
        self.gridline.set_clip_path(clippath, transform)
    set_clip_path.__doc__ = artist.Artist.set_clip_path.__doc__

class SkewXAxis(maxis.XAxis):
    #Copyright (c) 2008 Ryan May
    def _get_tick(self, major):
        return SkewXTick(self.axes, 0, '', major=major)

    def draw(self, renderer, *args, **kwargs):
        'Draw the axis lines, grid lines, tick lines and labels'
        ticklabelBoxes = []
        ticklabelBoxes2 = []

        if not self.get_visible(): return
        renderer.open_group(__name__)
        interval = self.get_view_interval()
        for tick, loc, label in self.iter_ticks():
            if tick is None: continue
            if transforms.interval_contains(interval, loc):
                tick.set_label1(label)
                tick.set_label2(label)
            tick.update_position(loc)
            tick.draw(renderer)
            if tick.label1On and tick.label1.get_visible():
                extent = tick.label1.get_window_extent(renderer)
                ticklabelBoxes.append(extent)
            if tick.label2On and tick.label2.get_visible():
                extent = tick.label2.get_window_extent(renderer)
                ticklabelBoxes2.append(extent)

        # scale up the axis label box to also find the neighbors, not
        # just the tick labels that actually overlap note we need a
        # *copy* of the axis label box because we don't wan't to scale
        # the actual bbox

        self._update_label_position(ticklabelBoxes, ticklabelBoxes2)

        self.label.draw(renderer)

        self._update_offset_text_position(ticklabelBoxes, ticklabelBoxes2)
        self.offsetText.set_text( self.major.formatter.get_offset() )
        self.offsetText.draw(renderer)

class SkewXAxes(Axes):
    #Copyright (c) 2008 Ryan May
    # The projection must specify a name.  This will be used be the
    # user to select the projection, i.e. ``subplot(111,
    # projection='skewx')``.
    name = 'skewx'

    def _init_axis(self):
        #Taken from Axes and modified to use our modified X-axis
        "move this out of __init__ because non-separable axes don't use it"
        self.xaxis = SkewXAxis(self)
        self.yaxis = maxis.YAxis(self)
        self._update_transScale()

    def draw(self, *args):
        '''
        draw() is overridden here to allow the data transform to be updated
        before calling the Axes.draw() method.  This allows resizes to be
        properly handled without registering callbacks.  The amount of
        work done here is kept to a minimum.
        '''
        self._update_data_transform()
        Axes.draw(self, *args)

    def _update_data_transform(self):
        '''
        This separates out the creating of the data transform so that
        it alone is updated at draw time.
        '''
        # This transforms x in pixel space to be x + the offset in y from
        # the lower left corner - producing an x-axis sloped 45 degrees
        # down, or x-axis grid lines sloped 45 degrees to the right
        self.transProjection.set(transforms.Affine2D(
            array([[1, 1, -self.bbox.ymin], [0, 1, 0], [0, 0, 1]])))

        # Full data transform
        self.transData.set(self._transDataNonskew + self.transProjection)

    def _set_lim_and_transforms(self):
        """
        This is called once when the plot is created to set up all the
        transforms for the data, text and grids.
        """
        #Get the standard transform setup from the Axes base class
        Axes._set_lim_and_transforms(self)

        #Save the unskewed data transform for our own use when regenerating
        #the data transform. The user might want this as well
        self._transDataNonskew = self.transData

        #Create a wrapper for the data transform, so that any object that
        #grabs this transform will see an updated version when we change it
        self.transData = transforms.TransformWrapper(
            transforms.IdentityTransform())

        #Create a wrapper for the proj. transform, so that any object that
        #grabs this transform will see an updated version when we change it
        self.transProjection = transforms.TransformWrapper(
            transforms.IdentityTransform())
        self._update_data_transform()

    def get_xaxis_transform(self, which='grid'):
        """
        Get the transformation used for drawing x-axis labels, ticks
        and gridlines.  The x-direction is in data coordinates and the
        y-direction is in axis coordinates.

        We override here so that the x-axis gridlines get properly
        transformed for the skewed plot.
        """
        return self._xaxis_transform + self.transProjection

    # Disable panning until we find a way to handle the problem with
    # the projection
    def start_pan(self, x, y, button):
        pass

    def end_pan(self):
        pass

    def drag_pan(self, button, key, x, y):
        pass

    def other_housekeeping(self,pmin=100.,mixratio=array([])):
	# Added by Thomas Chubb
	self.yaxis.grid(True,ls='-',color='y',lw=0.5)
	for TT in linspace(-100,100,21):
	    self.plot([TT,TT],[1000,pmin],color='y',lw=0.5)
	self.set_ylabel('Pressure (hPa)')
	self.set_xlabel('Temperature (C)')
	self.set_yticks(linspace(100,1000,10))
	self.yaxis.set_major_formatter(ScalarFormatter())
	self.set_xlim(-40,30)
	self.set_ylim(1013.,pmin)

    def set_xticklocs(self,xticklocs):
	# Added by Thomas Chubb
	self.set_xticks(xticklocs)

    def add_dry_adiabats(self,T0,P,**kwargs):
	# Added by Thomas Chubb
	P0=P[0]
	T=array([ (st+273.15)*(P/P0)**(R/Cp)-273.15 for st in T0 ])
	if kwargs.has_key('color'): 
	    col=kwargs['color']
	else: 
	    col='k'
	for tt in T:
	    self.plot(tt,P,**kwargs)
	    if (tt[8]>-50) and (tt[8]<20):
		self.text(tt[8],P[8]+10,'%d'%(tt[0]+273.15),fontsize=8,ha='center',va='bottom',\
			rotation=-30,color=col,\
			bbox={'facecolor':'w','edgecolor':'w'})

    def add_moist_adiabats(self,T0,P,**kwargs):
	# Added by Thomas Chubb
	T=array([LiftWet(st,P) for st in T0])
	if kwargs.has_key('color'): 
	    col=kwargs['color']
	else: 
	    col='k'
	for tt in T:
	    self.plot(tt,P,**kwargs)
	    # if (tt[-1]>-60) and (tt[-1]<-10):
	    self.text(tt[-1],P[-1],'%d'%tt[0],ha='center',va='bottom',\
		    fontsize=8,\
		    bbox={'facecolor':'w','edgecolor':'w'},color=col)

    def add_mixratio_isopleths(self,w,P,**kwargs):
	# Added by Thomas Chubb
	e=array([P*ww/(.622+ww) for ww in w])
	T = 243.5/(17.67/log(e/6.112) - 1)
	if kwargs.has_key('color'): 
	    col=kwargs['color']
	else: 
	    col='k'
	for tt,mr in zip(T,w):
	    self.plot(tt,P.flatten(),**kwargs)
	    if (tt[-1]>-45) and (tt[-1]<20):

		if mr*1000<1.:
		    fmt="%4.1f"
		else:
		    fmt="%d"

		self.text(tt[-1],P[-1],fmt%(mr*1000),\
			color=col, fontsize=8,ha='center',va='bottom',\
			bbox={'facecolor':'w','edgecolor':'w'})
		# self.text(tt[0],1000,'%4.1f'%mr*1000)

# Now register the projection with matplotlib so the user can select
# it.
register_projection(SkewXAxes)

class Sounding(UserDict):
    # Copyright (c) 2013 Thomas Chubb 
    """Utilities to read, write and plot sounding data quickly and without fuss
    
    INPUTS:
    filename:   If creating a sounding from a file, the full file name. The 
		format of this file is quite pedantic and needs to conform 
		to the format given by the University of Wyoming soundings 
		(see weather.uwyo.edu/upperair/sounding.html) 
    data: 	Soundings can be made from atmospheric data. This should be 
		in the form of a python dict with (at minimum) the following 
		fields:

		TEMP: dry-bulb temperature (Deg C)
		DWPT: dew point temperature (Deg C)
		PRES: pressure (hPa)
		SKNT: wind speed (knots)
		WDIR: wind direction (deg)

		The following fields are also used, but not required by the 
		plot_skewt routine:

		HGHT (m)
		RELH (%)
		MIXR (g/kg)
		THTA (K)
		THTE (K)
		THTV (K)
    """


    def __init__(self,filename=None,data=None):
	UserDict.__init__(self)

	if data is None:
	    self['data']={}
	    self.readfile(filename)
	else:
	    self['data']=data
	    self['SoundingDate']=""

    def plot_skewt(self, imagename=None, title=None):
	'''
	If you want to plot a skewt, Sounding.plot_skewt

	Inputs:
	    p -> 1d numpy array, pressure in Pa/100.0 (hPa)
	    h -> 1d numpy array, height in m
	    t -> 1d numpy array, temp in C
	    td -> 1d numpy array, dew pt temp in C
	    imagename -> string, the name you want to call the image ... i.e. louise.png

	Optional Inputs:
	    title -> string, obvious really
	    show -> True/False, if True will open and show plot, if false, will just save to image file.

	Example usage:
	    Sounding.plot_skewt(p/100.0 (Grrr), h, t (C), td (C), 'louse.png', title = 'woo.png', show = False)
	
	'''

	fig,ax,wbax=self.make_skewt_axes()
	self.add_profile(fig,ax,wbax,color='r',lw=2,)

	if isinstance(title, str):
	    ax.set_title(title)
	else:
	    ax.set_title(self['SoundingDate'])

	if imagename is not None:
	    print("saving figure")
	    fig.savefig(imagename,dpi=100)

	return fig,ax,wbax

    def add_profile(self,fig,ax,wbax,bloc=0.5,**kwargs):
	"""After-market hack to add multiple profiles to the same plot.


	It's the same routine as plot_skewt, but requires fig, ax and wbax
	from the make_skewt_axes function as inputs.
	"""

	assert self['data'].has_key('pres'), "Pressure in hPa (PRES) is required!"
	p = self['data']['pres']

	assert self['data'].has_key('temp'), "Temperature in C (TEMP) is required!"


	try:
	    assert self['data'].has_key('drct')
	    assert self['data'].has_key('sknt')
	    rdir = (270.-self['data']['drct'])*(pi/180.)
	    uu = self['data']['sknt']*cos(rdir)
	    vv = self['data']['sknt']*sin(rdir)
	except AssertionError:
	    print "Warning: No SKNT/DRCT available"
	    uu=ma.zeros(p.shape)
	    vv=ma.zeros(p.shape)

	tcprof=ax.semilogy(self['data']['temp'], self['data']['pres'],zorder=5,**kwargs)
	try:
	    dpprof=ax.semilogy(self['data']['dwpt'], self['data']['pres'],zorder=5,**kwargs)
	except KeyError:
	    print "Warning: No DWPT available"

	nbarbs=(~uu.mask).sum()

	skip=max(1,int(nbarbs/32))

	# if kwargs.has_key('color'): bcol=kwargs['color']
	# else: bcol='k'

	if kwargs.has_key('alpha'): balph=kwargs['alpha']
	else: balph=1.

	wbax.barbs((zeros(p.shape)+bloc)[::skip]-0.5, p[::skip], uu[::skip], vv[::skip],\
		length=6,color='k',alpha=balph)

	ax.other_housekeeping()
	wbax.set_xlim(-1.5,1.5)

	return tcprof

    def make_skewt_axes(self,pmin=100.):
	fig = figure(figsize=(8,8))
	fig.clf()
	
	rcParams.update({\
		'axes.linewidth':1,\
		'axes.edgecolor':'y',\
		'ytick.color':'k',\
		'xtick.color':'k',\
		'font.size':10,\
		'ytick.major.size':0,\
		'ytick.minor.size':0})

	ax=fig.add_axes([.135,.1,.815,.8], projection='skewx')
	ax.set_yscale('log')

	xticklocs=arange(-80,45,10)
	T0 = xticklocs
	P0 = 1050.

	P=linspace(1013.,pmin,37)

	w = array([0.0001,0.0004,0.001, 0.002, 0.004, 0.007, 0.01, 0.016, 0.024, 0.032])
	ax.add_mixratio_isopleths(w,P[P>=700],color='g',ls='--',alpha=1.,lw=0.5)
	ax.add_dry_adiabats(linspace(250,440,20)-273.15,P,color='g',ls='--',alpha=1.,lw=0.5)
	ax.add_moist_adiabats(linspace(8,32,7),P[P>=200],color='g',ls='--',alpha=1.,lw=0.5)

	wbax=fig.add_axes([0.85,0.1,0.1,0.8],sharey=ax,frameon=False)

	wbax.xaxis.set_ticks([],[])
	wbax.yaxis.grid(True,ls='-',color='y',lw=0.5)
	for tick in wbax.yaxis.get_major_ticks():
	    tick.label1On = False
	wbax.set_xlim(-1.5,1.5)

	ax.other_housekeeping(pmin=pmin)

	hax=fig.add_axes([0.175,0.1,0.,0.8],frameon=True)
	hax.xaxis.set_ticks([],[])
	hax.spines['left'].set_color('k')
	hax.spines['right'].set_visible(False)
	hax.tick_params(axis='y', colors='k',labelsize=8)
	hax.set_ylim(0,16.18)
	hax.set_title("km/kft",fontsize=10)

	hay=hax.twinx()
	hay.xaxis.set_ticks([],[])
	hay.tick_params(axis='y', colors='k',labelsize=8)
	hay.set_ylim(0,53.084)


	return fig,ax,wbax

    def readfile(self,fname):
	#--------------------------------------------------------------------
	# This *should* be a convenient way to read a uwyo sounding
	#--------------------------------------------------------------------
	fid=open(fname)
	lines=fid.readlines()
	nlines=len(lines)
	ndata=nlines-34
	output={}

	fields=lines[3].split()
	units=lines[4].split()

	# First line for WRF profiles differs from the UWYO soundings
	header=lines[0]
	if header[:5]=='00000':
	    # WRF profile
	    self['StationNumber']='-99999'
	    self['Longitude']=float(header.split()[5].strip(","))
	    self['Latitude']=float(header.split()[6])
	    self['SoundingDate']=header.split()[-1]
	else:
	    self['StationNumber']=header[:5]
	    dstr=(' ').join(header.split()[-4:])
	    self['SoundingDate']=datetime.strptime(dstr,"%HZ %d %b %Y").strftime("%Y-%m-%d_%H:%M:%S") 

	for ff in fields:
	    output[ff.lower()]=zeros((nlines-34))-999.

	lhi=[1, 9,16,23,30,37,46,53,58,65,72]
	rhi=[7,14,21,28,35,42,49,56,63,70,77]

	lcounter=5
	for line,idx in zip(lines[6:],range(ndata)):
	    lcounter+=1

	    try: output[fields[0].lower()][idx]=float(line[lhi[0]:rhi[0]])
	    except ValueError: break
	    
	    for ii in range(1,len(rhi)):
		try: 
		    # Debug only:
		    # print fields[ii].lower(), float(line[lhi[ii]:rhi[ii]].strip())
		    output[fields[ii].lower()][idx]=float(line[lhi[ii]:rhi[ii]].strip())
		except ValueError: 
		    pass

	for field in fields:
	    ff=field.lower()
	    self['data'][ff]=ma.masked_values(output[ff],-999.)

	return None
 
def LiftWet(startt,pres):
    #--------------------------------------------------------------------
    # Lift a parcel moist adiabatically from startp to endp.
    # Init temp is startt in C.      
    #--------------------------------------------------------------------

#     temp=zeros(pres.shape)
#     temp[0]=startt
#     delp=diff(pres)
# 
#     ii=0
#     for pp,dp in zip(pres[1:],delp):
# 	ii+=1
# 	temp[ii]=temp[ii-1]-100*dp*gammaw(temp[ii-1],pp-dp/2,100)

    temp=startt
    t_out=zeros(pres.shape);t_out[0]=startt
    for ii in range(pres.shape[0]-1):
	delp=pres[ii]-pres[ii+1]
 	temp=temp-100*delp*gammaw(temp,pres[ii]-delp/2,100)
	t_out[ii+1]=temp

    return t_out

def gammaw(tempc,pres,rh):
    #-----------------------------------------------------------------------
    # Function to calculate the moist adiabatic lapse rate (deg C/Pa) based
    # on the temperature, pressure, and rh of the environment.
    #----------------------------------------------------------------------

    tempk=tempc+273.15
    es=SatVap(tempc)/100.
    ws=MixRatio(es,pres)
    w=rh*ws/100
    tempv=VirtualTemp(tempk,w)
    latent=Latentc(tempc)

    A=1.0+latent*ws/(287.05*tempk)
    B=1.0+0.622*latent*latent*ws/(1005*287.05*tempk*tempk)
    Density=100*pres/(287.05*tempv)
    Gamma=(A/B)/(1005.*Density)
    return Gamma

# def virtual(temp,mix):
    #------------------------------------------------------------
    # Function to return virtual temperature given temperature in 
    # kelvin and mixing ratio in g/g.
    #-------------------------------------------------------------
    # return temp*(1.0+0.6*mix)

# def latentc(tempc):
    #-----------------------------------------------------------------------
    # Function to return the latent heat of condensation in J/kg given
    # temperature in degrees Celsius.
    #-----------------------------------------------------------------------
    # return 1000*(2502.2-2.43089*tempc)

# def satvap2(temp):
    #---------------------------------------------------------------
    # Given temp in Celsius, returns saturation vapor pressure in mb
    #---------------------------------------------------------------
    # return 6.112*exp(17.67*temp/(temp+243.5))

# def mixratio(e,p):
    #------------------------------------------------------
    # Given vapor pressure and pressure, return mixing ratio
    #-------------------------------------------------------
    # return 0.622*e/(p-e)


if __name__=='__main__':

    sounding=Sounding("../examples/94975.2013070200.txt")
    sounding.plot_skewt("../examples/94975.2013070200.png")

