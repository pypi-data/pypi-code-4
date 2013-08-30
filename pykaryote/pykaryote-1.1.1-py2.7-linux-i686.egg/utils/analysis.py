"""
The analysis module is responsible for tracking and displaying the data from a 
BC simulation. There are two classes, Analyzer which is used to read and 
display stored data, and CreativeAnalyzer which extends Analyzer to allow 
tracking and storing data.
"""
from __future__ import division
from subprocess import call, PIPE

from pylab import *
import matplotlib.pyplot as plt
import matplotlib as mpl
from numpy import array, cumsum, arange, savetxt, concatenate, reshape
import numpy as np
import os
import shutil
import os.path
import time
import warnings

from pykaryote.utils.globals import settings as gv
from pykaryote.utils import environment_draw

color_list = ['blue', 'green', 'red', 'aqua', 'purple', 'yellow',
'black', 'fuchsia', 'gray', 'lime', 'maroon', 'navy', 'olive', 'teal',
'orange', 'silver']

mpl.rcParams['axes.color_cycle'] = color_list

# the spacing from top and bottom for the percentiles
percentile = 0.25

def aggregate_batch(analyzer_dirs, output_analyzer_dir):
    """Aggregate a batch of analyzer directories into a single analyzer
    directory by averaging them.
    """
    ann = Analyzer(analyzer_dirs)
    if not os.path.exists(output_analyzer_dir):
        os.makedirs(output_analyzer_dir)
    for metric_datafile in os.listdir(analyzer_dirs[0]):
        if metric_datafile in ['seed', 'used.cfg', 'num_runs', 'environment.npy']:
            continue
        out_path = os.path.join(output_analyzer_dir, metric_datafile)
        if metric_datafile[:27] == 'time_spent_in_gaussian_gen_':
            # aggregate ``time_spent_in_gaussian_gen`` data
            # data is combined into a 3 dimensional array
            # the first dimension is the run number
            # the second and third dimensions hold the data from that run
            data = ann.quick_read(metric_datafile, mode='split')
            np.save(out_path, data)
        elif metric_datafile[:11] == 'gens_until_':
            mean, stddev, blanks = ann.quick_read(metric_datafile, 
                                                    mode='threshold')
            np.savetxt(out_path, mean)
            np.savetxt('{}.stddev'.format(out_path), stddev)
            np.savetxt('{}.blanks'.format(out_path), blanks)
        else:
            try:
                metric_average = ann.quick_read(metric_datafile)
                np.savetxt(out_path, metric_average)
            except ValueError:
                # file was not a metric datafile, ignore it
                continue
    # record number of runs
    with open(os.path.join(output_analyzer_dir, 'num_runs'), 'w') as f:
        f.write('{}'.format(len(ann.base)))


class Analyzer(object):
    """Reads and plots data collected from a simulation.

    The Analyzer class defines methods for reading and plotting simulation 
    data. Data is read from the files created by a CreativeAnalyzer.
    
    src/analyze.py is a command line usable script to use Analyzer to display 
    stored data.
    
    Note that the various ``plot_...`` methods provided by Analyzer are
    functionally equivalent to a pylab ``plot([some data])`` command. 
    (although they do set their own title)
    
    *Args*: ``data_folders (list)``: A list of strings for the directory(s) 
             containing the analysis data. Can be 1 simulations analyzer/ or 
             multiple ones (but with compatible config file)
        
    *Data*:
        The Analyzer provides access to the analysis data. This access is 
        provided through quick_read(data) and export_as_csv(data). The options 
        for data are:
        
        * ``fitness`` - Average fitness
        
        * ``genome_length`` - Average genome length
        
        * ``chemicals`` - Average amount of each chemical owned
        
        * ``time_spent`` - Breakdown of proportional time spent gathering, 
          moving, building
        
        * ``failed_builds`` - Moles of attempted-protein that were returned 
          because of a lack of resources to finish
        
        * ``complexes`` - Average amount of complexes, broken down by length
        
        * ``complex_diversity`` - Average number of unique complexes, 
          broken down by length
        
        * ``complexes_invented`` - Total number of complexes invented, 
          broken down by length
        
        * ``family_sizes`` - Average family size, broken down by length
        
        * ``family_lengths`` - Number of families, broken down by length
        
        * ``chemical_complexity`` - Complexity score of each chemical. See 
          :py:meth:`compute_chem_complexity()` documentation for details
        
        * ``percent_functional`` - Percent of complexes in use that are 
          functional.
          See :py:meth:`percent_functional()` for more details
        
        * ``component_percent_functional`` - Percent of components of functional
          complexes that are themselves functional.
        
        * ``<#>ancestors`` where # is the number of generations back specified 
          by globals - Number of organisms contributing to the genome # 
          generations ahead
        
        * ``complexity`` - Complexity score of each organism. See 
          :py:meth:`compute_complexity`
        
        * ``irreducible_complexity``- Irreducible complexity score of each 
          organism. See :py:meth:`compute_complexity`
        
        * ``num_distinct_complexes_current``
        
        * ``num_distinct_complexes_current_functional``
        
        * ``num_distinct_complexes_current_nonfunctional``
        
        * ``num_distinct_complexes_ever`` - synonymous with ``complexes_invented``
        
        * ``num_distinct_complexes_ever_functional``
        
        * ``num_distinct_complexes_ever_nonfunctional``
        
        * ``num_families_current``
        
        * ``num_families_current_functional``
        
        * ``num_families_current_nonfunctional``
        
        * ``num_families_ever``
        
        * ``num_families_ever_functional``
        
        * ``num_families_ever_nonfunctional``
        
    """

    def __init__(self, data_folders):
        """Initializes an analyzer.
        Args:
            data_folders: a list of paths to simulation data directories.
        """
        if data_folders == [] or data_folders is None:
            raise Exception("Analyzer must be provided with a list of data "\
                            "folders")
        # if only a string was passed, treat it as a single item list
        if type(data_folders) == str:
            data_folders = [data_folders]

        self.base = data_folders
        try:
            if not gv.is_initialized:
                gv.init_globals(os.path.join(self.base[0], "used.cfg"))
        except:
            raise Exception("Failed to read config: %s" % (
                            os.path.join(self.base[0], "used.cfg")))
        if len(data_folders) == 1:
            self.single = True
        else:
            self.single = False
        # ignore warnings from empty graphs
        warnings.filterwarnings('ignore', r'.*Attempting to set identical '\
                                'bottom==top results.*')
        
    def plot_fitness(self, breakdown = True, **kwargs):
        """
        Plots the average fitness
        
        *Args*:
        
            ``breakdown`` (bool): For single runs, this plot can show regions 
            marking min, lower Q, average, upper Q, max. To disable this feature
            and plot only the average line, set breakdown to False 
            
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/fitness.png
            :scale: 50 %
            
        """
        
        if self.single:
            if breakdown:
                min = self.quick_read("fitness_min")
                num = len(min)
                lower = self.quick_read("fitness_lower")[:num]
                avg = self.quick_read("fitness_avg")[:num]
                upper = self.quick_read("fitness_upper")[:num]
                max = self.quick_read("fitness_max")[:num]
                x = arange(0,len(avg))
                fill_between(x, min, max, alpha=0.1)
                fill_between(x, lower, upper, alpha=0.2)
                plot(avg)
            else:
                avg = self.quick_read("fitness_avg")
                plot(avg)
        else:
            min, lower, avg, upper, max = self.quick_read("fitness_avg", 
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            fill_between(x, min, max, alpha=0.1)
            fill_between(x, lower, upper, alpha=0.2)
            plot(avg)
        title("Average Fitness")

    def plot_complexity_and_fitness(self, breakdown=True, 
                                    mass_mode=False, **kwargs):
        """Plots two graphs: one of fitness and one of complexity

        *Args*:
        
            ``breakdown`` (bool): For single runs, this plot can show regions 
            marking min, lower Q, average, upper Q, max. To disable this feature
            and plot only the average line, set breakdown to False 
            
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function

        """
        subplot(211)
        self.plot_fitness(breakdown = True, **kwargs)
        subplot(212)
        self.plot_complexity(breakdown = True, mass_mode = False, **kwargs)
        
    def plot_genome_length(self, breakdown = True, **kwargs):
        """
        Plots the average genome length
        
        *Args*:
        
            ``breakdown`` (bool): For single runs, this plot can show regions 
            marking min, lower Q, average, upper Q, max. To disable this feature
            and plot only the average line, set breakdown to False 
            
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/genome.png
            :scale: 50 %
        """
        if self.single:
            if breakdown:
                min = self.quick_read("genome_length_min")
                num = len(min)
                lower = self.quick_read("genome_length_lower")[:num]
                avg = self.quick_read("genome_length_avg")[:num]
                upper = self.quick_read("genome_length_upper")[:num]
                max = self.quick_read("genome_length_max")[:num]
                x = arange(0,len(avg))
                fill_between(x, min, max, alpha=0.1)
                fill_between(x, lower, upper, alpha=0.2)
                plot(avg)
            else:
                avg = self.quick_read("genome_length_avg")
                plot(avg)
        else:
            min, lower, avg, upper, max = self.quick_read("genome_length_avg", 
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            fill_between(x, min, max, alpha=0.1)
            fill_between(x, lower, upper, alpha=0.2)
            plot(avg)
        title("Average Genome Length")
        ylim(ymin=0)
        
    def plot_avg_time_spent(self, **kwargs):
        """
        Plots the average time spent on each type of action. The white section
        corresponds to the time spent switching modes in which no useful work
        is done.
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/time_spent.png
            :scale: 50 %
        """
        y_data = self.quick_read("time_spent").transpose()/gv.generation_length
        y_data_stacked = cumsum(y_data, axis = 0)
        x = arange(0, len(y_data[0]))
        fill_between(x, 0, y_data_stacked[0,:], 
                     facecolor = (.1,.5,.1), alpha=0.7)
        fill_between(x, y_data_stacked[0,:], y_data_stacked[1,:], 
                     facecolor=(.3,.3,.8), alpha=0.7)
        fill_between(x, y_data_stacked[1,:], y_data_stacked[2,:], 
                     facecolor=(1,.3,.3))
        plot(y_data_stacked[0,:], label = "gather", color = (0,.5,0),**kwargs)
        plot(y_data_stacked[1,:], label = "move", color = (0,0,.8),**kwargs)
        plot(y_data_stacked[2,:], label = "build", color = (1,0,0),**kwargs)
        legend(loc=3, borderaxespad=0.)
        title("Time spent on each action")
        
    def plot_failed_builds(self, **kwargs):
        """
        Plots the average number of moles of attempted-protein that were 
        returned due to insufficient resources to finish.
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        """
        if self.single:
            data = self.quick_read("failed_builds")
            plot(data, **kwargs)
        else:
            min, lower, avg, upper, max = self.quick_read("failed_builds", 
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            fill_between(x, min, max, facecolor = color_list[0], 
                         alpha=0.2, edgecolor = "white")
            fill_between(x, lower, upper, facecolor = color_list[0], 
                         alpha=0.2, edgecolor = "white")
            plot(avg, color = color_list[0])
        xlabel("generations")
        ylabel('moles')
        title("Average moles of failed attempted-protein")
        
    def plot_gen_time(self, **kwargs):
        """
        Plots the time taken by each generation.
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        """
        if self.single:
            data = self.quick_read("gen_time")
            plot(data, **kwargs)
        else:
            min, lower, avg, upper, max = self.quick_read("gen_time", 
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            fill_between(x, min,   max,   facecolor = color_list[0], 
                         alpha=0.2, edgecolor = "white")
            fill_between(x, lower, upper, facecolor = color_list[0], 
                         alpha=0.2, edgecolor = "white")
            plot(avg, color = color_list[0])
        xlabel("generations")
        ylabel('time (seconds)')
        title("Time per generation")
        
    def plot_chemicals(self, **kwargs):
        """
        Plots the average number of each chemical owned by organisms in each 
        generation
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/chemicals.png
            :scale: 50 %
        """
        subplots_adjust(right = .8)
        data = self.quick_read("chemicals") + 1
        for c in range(gv.num_chemicals):
            semilogy([gen[c] for gen in data], label=str(c), **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., 
               title = "Chem #")
        title("Average production of chemicals")
        
    def plot_complexes(self, **kwargs):
        """
        Plots the average units of complexes owned by an organism, broken down
        by complex length.
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/complexes.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        data = self.quick_read("complexes") + 1
        if gv.max_complex_length > 1:
            for c in range(gv.max_complex_length): 
                semilogy(data[: , c], label = str(c+1), **kwargs)
        else:
            semilogy(data,label = "1", **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., 
               title = "Length")
        title("Average units of complexes")
        
    def plot_complex_diversity(self, **kwargs):
        """
        Plots the average number of distinct complexes of each length
        owned by an organism
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/complex_diversity.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        data = self.quick_read("complex_diversity")
        if gv.max_complex_length > 1:
            for c in range(gv.max_complex_length): 
                plot(data[:,c],label = str(c+1), **kwargs)
        else:
            plot(data,label = "1", **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., 
               title = "Length")
        title("Number of complexes per organism")
    
    def plot_invented_complexes(self, **kwargs):
        """
        Plots the total number of complexes invented
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/invented_complexes.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        if self.single:
            data = self.quick_read("complexes_invented")
            if gv.max_complex_length > 1:
                for c in range(gv.max_complex_length): 
                    plot(data[:,c],label = str(c+1), **kwargs)
            else:
                plot(data,label = "1", **kwargs)
        else:
            min, lower, avg, upper, max = self.quick_read("complexes_invented", 
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            for c in range(gv.max_complex_length):
                fill_between(x, min[:,c], max[:,c], \
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                fill_between(x, lower[:,c], upper[:,c], 
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                plot(avg[:,c],color = color_list[c],label = str(c+1))
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
               title = "Length")
        title("Number of complexes invented")
        ylim(ymin=0)
        
    def plot_percent_functional(self, **kwargs):
        """
        Plots the percent of complexes that are functional
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/percent_functional.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        data = self.quick_read("percent_functional")
        if gv.max_complex_length > 1:
            for c in range(gv.max_complex_length): 
                plot(data[:,c],label = str(c+1), **kwargs)
        else:
            plot(data,label = "1", **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        title("Percent of complexes that are functional")
        ylim(ymin=0, ymax = 1)
        
    def plot_component_percent_functional(self, **kwargs):
        """
        Plots the percent of components of complexes that are functional
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/comp_perc_func.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        if self.single:
            data = self.quick_read("component_percent_functional")
            if gv.max_complex_length > 1:
                for c in range(gv.max_complex_length): 
                    plot(data[:,c],label = str(c+1), **kwargs)
            else:
                plot(data,label = "1", **kwargs)
            legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
                   title = "Length")
            title("Percent of complex-components that are functional")
        else:
            data_array = self.quick_read("component_percent_functional",
                                         aggregate = False)
            
        ylim(ymin=0, ymax = 1)
        
    def plot_family_sizes(self, **kwargs):
        """
        Plots the average size of families of each length
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/fam_size.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        data = self.quick_read("family_sizes") + .1
        if gv.max_complex_length > 1:
            for c in range(gv.max_complex_length): 
                semilogy(data[:,c],label = str(c+1), **kwargs)
        else:
            semilogy(data,label = "1", **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., 
               title = "Length")
        title("Average Family Size")
        
    def plot_family_lengths(self, **kwargs):
        """
        Plots the number of families of each length
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/fam_length.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        if self.single:
            data = self.quick_read("family_lengths")
            if gv.max_complex_length > 1:
                for c in range(gv.max_complex_length): 
                    plot(data[:,c],label = str(c+1), **kwargs)
            else:
                plot(data,label = "1", **kwargs)
        else:
            min, lower, avg, upper, max = self.quick_read("family_lengths",
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            for c in range(gv.max_complex_length):
                fill_between(x, min[:,c], max[:,c], \
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                fill_between(x, lower[:,c], upper[:,c], 
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                plot(avg[:,c],color = color_list[c],label = str(c+1))
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
               title = "Length")
        title("Number of Families of a given length")
        ylim(ymin = 0)
        
    def plot_chemical_complexity(self, **kwargs):
        """
        Plots the average complexity value for each chemical
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/chemical_complexity.png
            :scale: 50 %
        """
        subplots_adjust(right = .8)
        data = self.quick_read("chemical_complexity")
        for c in range(gv.num_chemicals):
            plot([gen[c] for gen in data], label=str(c), **kwargs)
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., 
               title = "Chem #")
        title("Average chemical complexity")
        
    def plot_ancestry(self, **kwargs):
        """
        Plots the number of organisms that contribute to the gene pool a few
        generations ahead. How many controlled by ``track_ancestors``.
        
        *Args*:
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/ancestry.png
            :scale: 50 %
        """
        subplots_adjust(right=.8)
        for back in gv.tracked_ancestors:
            try:
                data = self.quick_read("%dancestors"%back)
                plot(data, label=str(back), **kwargs)
            except IOError:
                pass
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        title("Number of contributers N generations ahead")
         
    def plot_num_distinct(self, comp_or_fam, timeframe="current", 
                          functional=None, derivative=False, **kwargs):
        """
        Plots the number of complexes/families that currently/have ever
        existed, and may be restricted to non- or functional.
        
        *Args*:
        
            ``comp_or_fam`` (str) either "complexes" or "families" 
            (only first letter necessary).
            
            ``timeframe`` (str) either "current" or "ever"
            
            ``functional`` whether to plot only functional rather than only 
            non-functional.  Both are printed if this is ``None``.
            
            ``derivative`` whether to plot the derivative.
            
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        """
        subplots_adjust(right=.8)
        comp_or_fam_arg = "complexes" if comp_or_fam[0]=='c' else "families"
        if functional:
            functional_arg = "_functional"
        elif functional == False:
            functional_arg = "_nonfunctional"
        else:
            functional_arg = ""
        file_to_read = "num_%s_%s%s" % (comp_or_fam_arg, timeframe, 
                                        functional_arg)
        if self.single:
            data = self.quick_read(file_to_read)
            if derivative:
                data = np.diff(data,axis=0)
            if gv.max_complex_length > 1:
                for c in range(gv.max_complex_length): 
                    plot(data[:,c],label = str(c+1), **kwargs)
            else:
                plot(data,label = "1", **kwargs)
        else:
            min, lower, avg, upper, max = self.quick_read(file_to_read,
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            for c in range(gv.max_complex_length):
                fill_between(x, min[:,c], max[:,c], \
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                fill_between(x, lower[:,c], upper[:,c], 
                    facecolor = color_list[c], alpha=0.2, edgecolor = "white")
                plot(avg[:,c],color = color_list[c],label = str(c+1))
        legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
               title = "Length")
        title('%sNumber of distinct %s at %s%s'%(
            ('Derivative of ' if derivative else ''), 
            comp_or_fam, 
            timeframe, 
            ('' if functional==None else " that are"+("" if functional else "n't")+" functional" )))
        xlabel("generations")
        ylabel("number of "+comp_or_fam)
        ylim(ymin=0)

        
    def plot_complexity(self, breakdown = True, mass_mode = False, **kwargs):
        """
        Plots the complexity, averaging over all chemicals.
        Does not weight based on chemical amounts or effectiveness.
        
        *Args*:
        
            ``breakdown`` (bool): For single runs, this plot can show regions 
            marking min, lower Q, average, upper Q, max. To disable this feature
            and plot only the average line, set breakdown to False 
            
            ``mass_mode`` (bool) - special options for mass_run's plot. 
            Default: ``False``
            
            ``**kwargs``: a list of keyword args that can be passed to the 
            plotting function
        
        .. image:: pics/complexity.png
            :scale: 50 %
        """
        if mass_mode:
            plot(self.quick_read("complexity_avg"),label = "complexity_avg",
                 **kwargs)
            title("Complexity average")
            ylim(ymin = 0)
            return 
        if self.single:
            if breakdown:
                min = self.quick_read("complexity_min")
                num = len(min)
                lower = self.quick_read("complexity_lower")[:num]
                avg = self.quick_read("complexity_avg")[:num]
                upper = self.quick_read("complexity_upper")[:num]
                max = self.quick_read("complexity_max")[:num]
                x = arange(0,len(avg))
                fill_between(x, min, max, alpha=0.1, color = color_list[0])
                fill_between(x, lower, upper, alpha=0.2, color = color_list[0])
                plot(avg, label = "complexity", color = color_list[0])
                min = self.quick_read("irreducible_complexity_min")[:num]
                lower = self.quick_read("irreducible_complexity_lower")[:num]
                avg = self.quick_read("irreducible_complexity_avg")[:num]
                upper = self.quick_read("irreducible_complexity_upper")[:num]
                max = self.quick_read("irreducible_complexity_max")[:num]
                x = arange(0,len(avg))
                fill_between(x, min, max, alpha=0.1, color = color_list[1])
                fill_between(x, lower, upper, alpha=0.2, color = color_list[1])
                plot(avg, label = "irreducible_complexity", 
                     color = color_list[1])
            else:
                avg = self.quick_read("complexity_avg")
                plot(avg, label = "complexity", color = color_list[0])
                avg = self.quick_read("irreducible_complexity_avg")
                plot(avg, label = "irreducible_complexity",
                     color = color_list[1])
        else:
            min, lower, avg, upper, max = self.quick_read("complexity_avg",
                                                          mode = "breakdown")
            x = arange(0,len(avg))
            fill_between(x, min, max, alpha=0.1, color = color_list[0])
            fill_between(x, lower, upper, alpha=0.2, color = color_list[0])
            plot(avg, color = color_list[0], label = "complexity")
            min, lower, avg, upper, max = self.quick_read(
                            "irreducible_complexity_avg", mode = "breakdown")
            fill_between(x, min, max, alpha=0.1, color = color_list[1])
            fill_between(x, lower, upper, alpha=0.2, color = color_list[1])
            plot(avg, color = color_list[1], label = "irr. complexity")
        legend(loc=2)
        title("Complexity")
        ylim(ymin = 0)

    def plot_time_spent_in_gaussian(self):
        """Plot how long each organism spent on each chemical.

        Creates a series of subplots where each bar corresponds to an
        the amount of time an organsim spent in each chemical gaussian.
        Each subplot in the series represents a single generation.

        ``data`` is a three dimentional array where::
            data[run_number, organism, gaussian_index] = number_of_codon_reads
                (number of codon reads while in that gaussian)
        """
        width = 0.35
        datafiles = []
        for filename in os.listdir(self.base[0]):
            if filename[:27] == 'time_spent_in_gaussian_gen_':
                datafiles.append(filename)
        gaussian_colors = []
        datafiles = sorted(datafiles, key=lambda x: int(x[27:-4]))
        for index, datafile in enumerate(datafiles):
            gen_number = int(datafile[27:-4])
            data = self.quick_read(datafile, mode='split', format='binary')
            # if this was a single run, we will need to add another dimension
            if len(data.shape) == 2:
                data = np.array([data])
            # if this was loaded from an aggregate, we will have an extra empty
            # dimension to remove
            if len(data.shape) == 4 and data.shape[0] == 1:
                data = data[0]
            # data must be three dimensional
            assert(len(data.shape) == 3)
            if index == 0:
                # initialize variables on first read
                num_runs = data.shape[0]
                plt.figure(figsize=(8*2*num_runs, 6*len(datafiles)))
                gaussian_colors = environment_draw.make_chemical_colors(
                                                        data.shape[2] -1,
                                                        format='matplotlib')
                # empty space uses a shade of grey
                gaussian_colors.append('0.9')
                ind = np.arange(data.shape[1])
            for run_num in range(num_runs):
                # plot data for run_num at generation gen_number
                subplot_num = num_runs*index+run_num+1
                plt.subplot(len(datafiles), num_runs, subplot_num)
                bottom = np.zeros(data.shape[1], dtype=float)
                for gaussian_index, gaussian_data in enumerate(data[run_num].T):
                    plt.bar(ind, gaussian_data,
                            color=gaussian_colors[gaussian_index],
                            bottom=bottom, width=width, align='center')
                    bottom += gaussian_data
                plt.ylabel('Time')
                plt.title('Time spent on chemical mound '\
                          '(generation {}, run {})'.format(gen_number, run_num))
                plt.xlabel('Organisms')
                plt.xticks(ind+width/2.0, range(len(ind)))

                legend_boxes = [Rectangle((0, 0), 1, 1, color=c)
                                for c in gaussian_colors]
                legend_labels = ['mound {}'.format(x)
                                 for x in range(len(legend_boxes))]
                legend_labels[-1] = 'no mound'
                plt.legend(legend_boxes, legend_labels, loc='best',
                           fancybox=True)

    def save_environment_drawing(self, out_dir):
        """Draws a picture of the chemical environment.

        This function does not use matplotlib.
        """
        grid = np.load(os.path.join(self.base[0], 'environment.npy'))
        environment_draw.draw_environment(grid, os.path.join(
                                        out_dir, 'environment.png'))

    def save_all(self, out_dir):
        """Plots and saves graphs of simulation data.
        """
        def save(name=None):
            """Saves a matplotlib figure to ``out_dir``.

            If ``name`` is not provided, use a numeric name: ``figure_x``.
            """
            if name is None:
                name = 'figure_{}'.format(save.fig_num)
                save.fig_num += 1
            plt.savefig(os.path.join(out_dir, name))

        save.fig_num = 1

        figure()
        subplot(211)
        self.plot_fitness()
        subplot(212)
        self.plot_genome_length()
        save()
        
        figure()
        self.plot_complexity()
        save()
        
        figure()
        self.plot_avg_time_spent()
        save()
        
        figure()
        self.plot_failed_builds()
        save()
        
        figure()
        self.plot_gen_time()
        save()

        self.plot_time_spent_in_gaussian()
        save('time_spent_in_gaussians')

        self.save_environment_drawing(out_dir)
        
        if gv.max_complex_length>0: #will break if no complexes
            figure()
            subplots_adjust(hspace=.25)
            subplot(211)
            self.plot_invented_complexes()
            subplot(212)
            self.plot_family_lengths()
            save()
            
            figure()
            subplot(211)
            self.plot_num_distinct("complexes",timeframe="current",
                                   functional=True)
            subplot(212)
            self.plot_num_distinct("complexes",timeframe="current",
                                   functional=False)
            save()
            
            figure()
            subplot(211)
            self.plot_num_distinct("complexes",timeframe="ever",functional=True)
            subplot(212)
            self.plot_num_distinct("complexes",timeframe="ever",
                                   functional=False)
            save()
            
            figure()
            subplot(211)
            self.plot_num_distinct("families",timeframe="current",
                                   functional=True)
            subplot(212)
            self.plot_num_distinct("families",timeframe="current",
                                   functional=False)
            save()
            
            figure()
            subplot(211)
            self.plot_num_distinct("families",timeframe="ever",functional=True)
            subplot(212)
            self.plot_num_distinct("families",timeframe="ever",functional=False)
            save()

            figure()
            subplot(211)
            self.plot_num_distinct("complexes",timeframe="ever",derivative=True)
            subplot(212)
            self.plot_num_distinct("families",timeframe="ever",derivative=True)
            save()

        # These graphs only make sense for single
        if self.single:
            figure()
            subplots_adjust(hspace=.25)
            subplot(211)
            self.plot_chemicals()
            subplot(212)
            self.plot_chemical_complexity()
            save()

            figure()
            subplot(111)
            self.plot_ancestry()
            save()

            figure()
            self.plot_time_spent_in_gaussian()
            save()
            
            if gv.max_complex_length>0: #will break if no complexes
                figure()
                subplots_adjust(hspace=.25)
                subplot(211)
                self.plot_complexes()
                subplot(212)
                self.plot_complex_diversity()
                save()
                
                figure()
                subplots_adjust(hspace=.25)
                subplot(211)
                self.plot_percent_functional()
                subplot(212)
                self.plot_component_percent_functional()
                save()
        
    def quick_read(self, data, mode = "standard", ndmin=1, format='text'):
        """Loads data as saved by the CreativeAnalyzer class.

        Reads from a simulation or batch of simulations.

        Average, mean, and standard deveation are calculated using the middle
        80%. Number of blanks uses the whole data set.
        
        *Args*:
        
            ``data`` (str): the data file to read from.
            
            ``mode`` (str): The reading mode. Options are:
                * ``standard`` returns the mean of multiple runs
                * ``threshold`` returns the mean, standard deviation, and 
                    number of simulations which did not reach the threshold.
                    Used to aggregate data specified in the [threshold-metrics]
                    section of a simulation's configuration file.
                * ``split`` returns data from multiple runs separately
                * ``stddev`` retuns tuple (avg, stddev)
                * ``breakdown`` returns a tuple (min, lower_part, avg, 
                    upper_part, max)
            ``format`` (str): File format to expect data in. Either 'text' or
                'binary'
            
        *Returns*:
            
            A numpy array
            *or*
            a tuple of arrays
        
        """
        all_data = []
        max_shape = []
        variable_shape = False
        if data[-4:] == '.npy':
            format = 'binary'
        for num, folder in enumerate(self.base):
            data_location = os.path.join(folder, data)
            if format == 'text':
                arr = np.loadtxt(data_location, dtype=float, ndmin=ndmin)
            elif format == 'binary':
                arr = np.load(data_location)
            all_data.append(arr)
            sim_data = all_data[-1]
            if num == 0:
                max_shape = list(sim_data.shape)
            # check if data has a variable shape
            # find the maximum for each dimension
            for i, size in enumerate(sim_data.shape):
                if len(max_shape) <= i:
                    variable_shape = True
                    max_shape.append(size)
                elif size > max_shape[i]:
                    variable_shape = True
                    max_shape[i] = size
                elif size != max_shape[i]:
                    variable_shape = True
        if variable_shape:
            # resize arrays to maximum size
            for i in range(len(all_data)):
                # 
                a = np.require(all_data[i], requirements='O')
                a.resize(max_shape, refcheck=False)
                all_data[i] = a
        data_array = np.array(all_data)
        if mode == "split":
            # return an array holding the array from each run
            return data_array
        data_array.sort(axis=0)
        if mode == "threshold":
            # calculate number of blanks (-1) in each row
            blanks = np.empty(data_array.shape[1], dtype=int)
            for row_num, row in enumerate(data_array.T):
                blanks[row_num] = np.searchsorted(row, [0.0])[0]
        # calculate middle 80 %
        # Note: this is not actually the middle 80%, it is an approximation,
        # where the upper and lower bounds are rounded.
        # An exact measure of the middle 80% would require taking the weighted
        # average of the bounds instead of rounding.
        # it was decided that rounding is a better solution, as it ensures
        # that actual data is used.
        lower_threshold = (1.0 - gv.mean_to_aggregate) / 2.0
        upper_threshold = gv.mean_to_aggregate + lower_threshold
        lower = int(data_array.shape[0] * lower_threshold)
        upper = int(ceil(data_array.shape[0] * upper_threshold))
        data_array = data_array[lower: upper]
        if mode == "standard":
            return np.average(data_array, axis=0)
        elif mode == "threshold":
            # return the mean, standard deviation, and number of blanks
            # for mean and standard deviation, blanks (-1) are replaced with
            # the max generation number
            if sum(blanks):
                # replace the blanks with the max generation number
                if not gv.generation_limit:
                    replacement = 5000.0
                else:
                    replacement = float(gv.generation_limit)
                data_array[data_array == -1.0] = replacement
            mean = np.mean(data_array, axis=0, dtype=int)
            stddev = np.std(data_array, axis=0, dtype=int)
            return mean, stddev, blanks
        elif mode == "stddev":
            return np.mean(data_array, axis=0), np.std(data_array, axis=0)
        elif mode == "breakdown":
            if self.single:
                raise Exception("Breakdown only valid for Analyzers with \
                                multiple runs")
            return breakdown(data_array)
        else:
            raise ValueError("Unrecognized mode: %s" % mode)
    
    def export_varialble_as_csv(self, data, output_file):
        """
        Converts an analyzer data log to csv.
        
        *Args*:
        
            ``data`` (str): the data file to read from.
            
            ``output_file`` (str): The filename of the new csv data
        
        """
        read_data = array(self.quick_read(data))
        savetxt(output_file, read_data, delimiter=",")
        
    def export_all_as_csv(self, output_file):
        """
        Exports all the analyzer data to a csv with headings. Note that for that 
        is separated by chemical number or complex length columns are created 
        for each chemical or length e.g. chemicals_0, chemicals_1,...
        
        All headings match the data variables discussed in the Analyzer class 
        documentation.
        
        *Args*:
        
            ``output_file`` (str): The filename of the new csv data
        """
        headings = "Generation, fitness_min, "
        fit = self.quick_read("fitness_min")
        data = concatenate( (reshape(arange(0,len(fit)),(-1,1)),
                           reshape(fit,(-1,1))) , axis = 1)
        data, headings = self.add_data(data, headings,"fitness_lower")
        data, headings = self.add_data(data, headings,"fitness_avg")
        data, headings = self.add_data(data, headings,"fitness_upper")
        data, headings = self.add_data(data, headings,"fitness_max")
        data, headings = self.add_data(data, headings,"genome_length_min")
        data, headings = self.add_data(data, headings,"genome_length_lower")
        data, headings = self.add_data(data, headings,"genome_length_avg")
        data, headings = self.add_data(data, headings,"genome_length_upper")
        data, headings = self.add_data(data, headings,"genome_length_max")
        data, headings = self.add_data(data, headings,"chemicals",
                                       gv.num_chemicals)
        #special handling
        data = concatenate((data, self.quick_read("time_spent")), axis = 1)
        headings += "time_gathering, time_moving, time_building, "
        data, headings = self.add_data(data, headings,"chemical_complexity",
                                       gv.num_chemicals)
        data, headings = self.add_data(data, headings,"complexes",
                                       gv.max_complex_length)
        data, headings = self.add_data(data, headings,"complex_diversity",
                                       gv.max_complex_length)
        data, headings = self.add_data(data, headings,"family_sizes",
                                       gv.max_complex_length)
        data, headings = self.add_data(data, headings,"family_lengths",
                                       gv.max_complex_length)
        data, headings = self.add_data(data, headings,"percent_functional",
                                       gv.max_complex_length)
        data, headings = self.add_data(data, headings,
                                       "component_percent_functional",
                                       gv.max_complex_length)
        for g in gv.tracked_ancestors:
            empty_column = np.zeros((len(data),1))
            headings += "ancestors_%d_ahead, "%g
            a_data = self.quick_read("%dancestors"%g)
            for i in range(len(a_data)):
                empty_column[i,0] = a_data[i]
            data = np.concatenate((data, empty_column), axis = 1)
            
        # make sure the directory exists
        try:
            out_path = os.path.split(output_file)[0]
            os.makedirs(out_path)
        except OSError:
            pass
        
        savetxt(output_file, data, delimiter=",")
        # work around to insert headings
        file = open(output_file,'r')
        data_str = file.read()
        file.close()
        file = open(output_file,'w')
        file.write(headings[:-2] + "\n" + data_str)
        file.close()
    
    def add_data(self, data, headings, name, number = 1):
        if number == 1:
            headings += name + ", "
            new_data = reshape(self.quick_read(name),(-1,1))
        else:
            headings += "".join([name+"_%d, "%i for i in range(number)])
            new_data = self.quick_read(name)
        data = concatenate(  (data,new_data ), axis = 1 )  
        return data, headings


class CreativeAnalyzer(object):
    """Saves data from a running simulation.

    Data, in the form of text files containing numpy arrays, are saved to 
    an 'analyzer' directory.
    
    *Args*:
        ``sim``: The simulation for which data will be recorded.
    """
    
    def __init__(self, sim):
        """
        Creates a CreativeAnalyzer for a simulation

        Args:
            sim: The simulation which this comparison is based off of.
            if sim.Comparison is true, this simulation is part of a comparison.
                In that case, don't calculate min, lower, and upper
                for metrics.
        """
        self.sim = sim
        self.base =  os.path.join(self.sim.data, self.sim.name, "analyzer")
        if not gv.is_initialized:
            gv.init_globals(os.path.join(self.base, "used.cfg"))
        gv.prevTime = time.time()
        # initialize lists to record the number of generations it takes for
        # a metric to reach a threshold value
        self._threshold_metrics = {}
        for metric, thresholds in zip(gv.metrics, gv.thresholds):
            l = [-1 for x in range(len(thresholds))]
            self._threshold_metrics[metric] = l
        # dictionary to hold the current value of each metric
        self._current_metric_values = {}
        self.__open_data_files()
        #write seed
        with open(os.path.join(self.base, "seed"), 'w') as f:
            f.write(str(gv.randomseed)+'\n')

    def __open_data_files(self):
        """Get open file handles to all data files.

        Open files are stored in self.data_files, a dictionary mapping
        metric_name `str` to a file like object.
        """
        self.data_files = {}
        metrics = ['fitness_avg', 'genome_length_avg', 'chemicals',
        'time_spent', 'complexes', 'complex_diversity', 'complexes_invented',
        'family_sizes', 'family_lengths', 'chemical_complexity',
        'percent_functional', 'component_percent_functional', 'complexity_avg',
        'irreducible_complexity_avg', 'failed_builds', 'num_complexes_current',
        'num_complexes_current_functional', 
        'num_complexes_current_nonfunctional', 'num_complexes_ever', 
        'num_complexes_ever_functional', 'num_complexes_ever_nonfunctional',
        'num_families_current', 'num_families_current_functional',
        'num_families_current_nonfunctional', 'num_families_ever', 
        'num_families_ever_functional', 'num_families_ever_nonfunctional',
        'gen_time']
        for prev_gen_number in gv.tracked_ancestors:
            metrics.append('%dancestors' % prev_gen_number)
        metrics_not_comparison = ['complexity_min', 'complexity_lower',
        'complexity_upper', 'complexity_max', 'irreducible_complexity_min',
        'irreducible_complexity_lower', 'irreducible_complexity_upper',
        'irreducible_complexity_max', 'fitness_min', 'fitness_lower',
        'fitness_upper', 'fitness_max', 'genome_length_min',
        'genome_length_lower', 'genome_length_upper', 'genome_length_max']
        for metric in metrics:
            filename = os.path.join(self.base, metric)
            self.data_files[metric] = open(filename, 'w')
        # don't track min, lower, upper, max when running a comparison
        if not self.sim.comparison:
            for metric in metrics_not_comparison:
                filename = os.path.join(self.base, metric)
                self.data_files[metric] = open(filename, 'w')

    def __del__(self):
        """Closes metric data files.
        """
        #TODO: use 'with' to open files. Don't explicitly close them.
        self.close_all()

    def save_as_data(self, ndarray, name, format='text'):
        """Saves the given array as a datafile with name ``name``.

        ``format`` (str): either 'text' or 'binary'

        If it is a 1 or 2d array, save in text format.
        If it has three or more dimensions, save in .np binary format.
        """
        if format == 'binary':
            np.save(os.path.join(self.base, name), ndarray)
        elif format == 'text':
            np.savetxt(os.path.join(self.base, name), ndarray)

    def close_all(self):
        """Closes metric data files.

        Also writes threshold metric data files.
        """
        for f in self.data_files.itervalues():
            f.close()
        # write threshold metric data
        for metric, values in self._threshold_metrics.iteritems():
            fname = os.path.join(self.base, 'gens_until_{}'.format(metric))
            with open(fname, 'w') as f:
                for gen_num in values:
                    f.write('{}\n'.format(gen_num))
        # write environment grid
        np.save(os.path.join(self.base, 'environment'),
                self.sim.environment.grid)
        
    def update(self):
        """
        Updates the Analyzer with data from a new generation
        """
        pts = array([org.fitness() for org in self.sim.organisms])
        # if this simulation is a comparison, only record the average
        if self.sim.comparison:
            self.quick_append('fitness_avg', np.average(pts))
        else:
            fi_min, fi_lower, fi_avg, fi_upper, fi_max = breakdown_points(pts)
            self.quick_append("fitness_min", fi_min)
            self.quick_append("fitness_lower", fi_lower)
            self.quick_append("fitness_avg", fi_avg)
            self.quick_append("fitness_upper", fi_upper)
            self.quick_append("fitness_max", fi_max)
        
        pts = array([len(org.genome) for org in self.sim.organisms])
        if self.sim.comparison:
            self.quick_append('genome_length_avg', np.average(pts))
        else:
            gl_min, gl_lower, gl_avg, gl_upper, gl_max = breakdown_points(pts)
            self.quick_append("genome_length_min", gl_min)
            self.quick_append("genome_length_lower", gl_lower)
            self.quick_append("genome_length_avg", gl_avg)
            self.quick_append("genome_length_upper", gl_upper)
            self.quick_append("genome_length_max", gl_max)
        
        chemall = [org.chemicals for org in self.sim.organisms]
        chemicals = [avg([chem[i] for chem in chemall]) 
                                            for i in range(gv.num_chemicals)]
        self.quick_append("chemicals", chemicals)
        
        moves = avg([org.moves for org in self.sim.organisms])
        gathers = avg([org.gathers for org in self.sim.organisms])
        builds = avg([org.builds for org in self.sim.organisms])
        self.quick_append("time_spent", [gathers, moves, builds])
        
        complexes = np.zeros(gv.max_complex_length, float)
        complex_diversity = np.zeros(gv.max_complex_length, float)
        for org in self.sim.organisms:
            for comp in org.complexes.values():
                complexes[comp.complex.length-1] += comp.amount
                complex_diversity[comp.complex.length-1] += 1
        complexes /= gv.num_organisms
        complex_diversity /= gv.num_organisms
        self.quick_append("complexes", list(complexes))
        self.quick_append("complex_diversity", list(complex_diversity))
        
        invented_complexes = [0 for _ in range(gv.max_complex_length)]
        for c in self.sim.environment.complexes.complex_lookup.values():
            invented_complexes[c.length-1] += 1
        self.quick_append("complexes_invented", invented_complexes)
        
        fam_sizes = [0 for _ in range(gv.max_complex_length)]
        fam_lengths = [0 for _ in range(gv.max_complex_length)]
        for fam in self.sim.environment.families.family_lookup.values():
            fam_sizes[fam.length-1] += fam.size
            fam_lengths[fam.length-1] += 1
        fam_sizes = [fam_sizes[i]/fam_lengths[i] if fam_lengths[i] !=0 else 0 for i in range(gv.max_complex_length)]
        self.quick_append("family_sizes", fam_sizes)
        self.quick_append("family_lengths", fam_lengths)
        
        chem_complexities = array([compute_chem_complexity(org) for org in self.sim.organisms])
        chem_comp = [sum(chem_complexities[:,i])/gv.num_organisms for i in range(gv.num_chemicals)]
        self.quick_append("chemical_complexity", chem_comp)
        
        p_func = array([percent_functional(org) for org in self.sim.organisms])
        avg_p_func = [sum(p_func[:,i])/gv.num_organisms for i in range(gv.max_complex_length)]
        self.quick_append("percent_functional", avg_p_func)
        
        c_p_func = array([component_percent_functional(org) for org in self.sim.organisms])
        avg_c_p_func = [sum(c_p_func[:,i])/gv.num_organisms for i in range(gv.max_complex_length)]
        self.quick_append("component_percent_functional", avg_c_p_func)
        
        ci_array = array([compute_complexity(org) for org in self.sim.organisms])
        if self.sim.comparison:
            c_avg = np.average(ci_array[:,0])
            ic_avg = np.average(ci_array[:,1])
            self.quick_append('complexity_avg', c_avg)
            self.quick_append('irreducible_complexity_avg', ic_avg)
        else:
            c_min, c_lower, c_avg, c_upper, c_max = breakdown_points(
                                                                ci_array[:,0])
            self.quick_append("complexity_min", c_min)
            self.quick_append("complexity_lower", c_lower)
            self.quick_append("complexity_avg", c_avg)
            self.quick_append("complexity_upper", c_upper)
            self.quick_append("complexity_max", c_max)
            ic_min, ic_lower, ic_avg, ic_upper, ic_max = breakdown_points(
                                                                ci_array[:,1])
            self.quick_append("irreducible_complexity_min", ic_min)
            self.quick_append("irreducible_complexity_lower", ic_lower)
            self.quick_append("irreducible_complexity_avg", ic_avg)
            self.quick_append("irreducible_complexity_upper", ic_upper)
            self.quick_append("irreducible_complexity_max", ic_max)
        
        #for finish_criteria
        self.sim.current_complexity_avg = c_avg
        self.sim.current_irreducible_complexity_avg = ic_avg
        
        for back in gv.tracked_ancestors:
            ancestor_set = set([]) # no duplicates
            for org in self.sim.organisms:
                #append the id of this org's ancestor `back` generations ago
                try:
                    ancestor_set.add(org.ancestry[-back])
                except IndexError:
                    pass
            self.quick_append("%dancestors"%back, len(ancestor_set))

        #failed_builds
        failed_builds = avg([org.failed_builds for org in self.sim.organisms])
        self.quick_append("failed_builds",failed_builds)

        #num distinct complexes current
        cur_complexes = set()
        for org in self.sim.organisms:
            for comp in org.complexes.values():
                cur_complexes.add((comp.complex))
        complexes = np.zeros(gv.max_complex_length, int)
        complexes_f  = np.zeros(gv.max_complex_length, int) #functional
        complexes_nf = np.zeros(gv.max_complex_length, int) #nonfunctional
        for comp in cur_complexes:
            complexes[comp.length-1]+=1
            if comp.is_functional:
                complexes_f[comp.length-1]+=1
            else:
                complexes_nf[comp.length-1]+=1
        self.quick_append("num_complexes_current",list(complexes))
        self.quick_append("num_complexes_current_functional",list(complexes_f))
        self.quick_append("num_complexes_current_nonfunctional",
                          list(complexes_nf))

        #num distinct complexes ever
        complexes = np.zeros(gv.max_complex_length, int)
        complexes_f  = np.zeros(gv.max_complex_length, int) #functional
        complexes_nf = np.zeros(gv.max_complex_length, int) #nonfunctional
        for comp in self.sim.environment.complexes.complex_lookup.values():
            complexes[comp.length-1]+=1
            if comp.is_functional:
                complexes_f[comp.length-1]+=1
            else:
                complexes_nf[comp.length-1]+=1
        self.quick_append("num_complexes_ever",list(complexes))
        self.quick_append("num_complexes_ever_functional",list(complexes_f))
        self.quick_append("num_complexes_ever_nonfunctional",list(complexes_nf))

        #num families current
        cur_fams = set()
        for org in self.sim.organisms:
            for comp in org.complexes.values():
                cur_fams.add((comp.complex.family))
        fams = np.zeros(gv.max_complex_length, int)
        fams_f = np.zeros(gv.max_complex_length, int) #functional
        fams_nf = np.zeros(gv.max_complex_length, int) #nonfunctional
        for fam in cur_fams:
            fams[fam.length-1]+=1
            if max(fam.function_vector) > gv.weak_factor*fam.length*gv.mutate_factor: #it's functional
                fams_f[fam.length-1]+=1
            else:
                fams_nf[fam.length-1]+=1
        self.quick_append("num_families_current",list(fams))
        self.quick_append("num_families_current_functional",list(fams_f))
        self.quick_append("num_families_current_nonfunctional",list(fams_nf))

        #num families ever
        fams = np.zeros(gv.max_complex_length, int)
        fams_f = np.zeros(gv.max_complex_length, int) #functional
        fams_nf = np.zeros(gv.max_complex_length, int) #nonfunctional
        for fam in self.sim.environment.families.family_lookup.values():
            fams[fam.length-1]+=1
            if (max(fam.function_vector) > 
                gv.weak_factor*fam.length*gv.mutate_factor):
                #it's functional
                fams_f[fam.length-1]+=1
            else:
                fams_nf[fam.length-1]+=1
        self.quick_append("num_families_ever",list(fams))
        self.quick_append("num_families_ever_functional",list(fams_f))
        self.quick_append("num_families_ever_nonfunctional",list(fams_nf))

        #gen_time
        curTime=time.time()
        try:
            self.quick_append("gen_time",curTime-gv.prevTime)
        except AttributeError:
            pass
        gv.prevTime=curTime

        # threshold metrics
        # Record how many generations it takes a metric to reach a threshold
        for metric, thresholds in zip(gv.metrics, gv.thresholds):
            for i, threshold in enumerate(thresholds):
                if (self._threshold_metrics[metric][i] == -1 and 
                    self._current_metric_values.get(metric, -1) >= threshold):
                    self._threshold_metrics[metric][i] = self.sim.generation

    def quick_append(self, metric, new_data):
        """
        Appends to the analyzer data logs.
        
        *Args*:
        
            ``metric`` (str): the name of the metric being recorded
            
            ``new_data``: The new data to add
        """
        self._current_metric_values[metric] = new_data
        if type(new_data) == list or type(new_data) == array: #strip brackets
            for value in new_data:
                self.data_files[metric].write('{} '.format(value))
            self.data_files[metric].write('\n')
        else:
            self.data_files[metric].write('{}\n'.format(new_data))
        
def avg(values):
    """
    Computes the arithmetic mean of a list
    """
    return sum(values, 0.0) / len(values)

def compute_chem_complexity(org):
    """
    Computes the "complexity" of each chemical for an organism. 
    Complexity is based on the contribution of complexes to the
    gathering of a chemical. 
    """
    comp_vec = np.zeros(gv.num_chemicals)
    
    for comp in org.complexes.values():
        comp_vec += comp.complex.function*comp.complex.length*comp.amount
    for i in xrange(gv.num_chemicals):
        #If the organism isn't benefitting, it's 0 complexity
        if comp_vec[i] > 0 and org.function[i] > 1: 
            #otherwise the formula fails for some cases
            comp_vec[i] = comp_vec[i]/org.function[i] 
        else:
            comp_vec[i] = 0
    return comp_vec
    
def percent_functional(org):
    """
    Examines the complexes produced by org and determines what percent of each
    length are functional.  Bases the percent on the number of unique complexes,
    not on the amounts in which they are produced.
    
    """
    func_vec = np.zeros(gv.max_complex_length)
    n_vec = np.zeros(gv.max_complex_length)
    for comp in org.complexes.values():
        i = comp.complex.length
        n_vec[i-1] += 1
        if comp.complex.is_functional:
            func_vec[i-1] += 1
    for i in range(gv.max_complex_length):
        if n_vec[i] == 0:
            n_vec[i] = 1
    return func_vec/n_vec
    
def component_percent_functional(org):
    """
    Examines the complexes produced by org and determines, for functional 
    complexes, what percent of protein components are functional
    """
    component_func_vec = np.zeros(gv.max_complex_length)
    component_n_vec = np.zeros(gv.max_complex_length)
    for comp in org.complexes.values():
        i = comp.complex.length
        if comp.complex.is_functional:
            if i > 1:
                component_n_vec[i-1] += 1
                # check which components are functional
                comp_funcs = [org.environment.complexes.get_complex(str([c])).is_functional for c in eval(comp.complex.name)]
                component_func_vec[i-1] += sum(comp_funcs)/i
                # bump up functional complexes w/ no functional bits so they can be seen
                if component_func_vec[i-1] == 0.0:
                    component_func_vec[i-1] = .005*i
    for i in range(gv.max_complex_length):
        if component_n_vec[i] == 0:
            component_n_vec[i] = 1
    return component_func_vec/component_n_vec
    
def compute_complexity(org):
    """
    Computes a score for the complexity and irreducible complexity of the 
    organism based on the complexity level of each chemical function.
    
    More information on computing complexities can be found in :ref:`complexity`
    """
    
    comp_vec = np.zeros(gv.num_chemicals)
    irr_comp_vec = np.zeros(gv.num_chemicals)
    
    for comp in org.complexes.itervalues():
        comp_vec += comp.complex.function*comp.complex.length*comp.amount
        if comp.complex.is_functional:
            #get the number of components that are not functional
            comp_funcs = [(1-org.environment.complexes.get_complex(str([c])).is_functional) for c in eval(comp.complex.name)]
            irr_comp_vec += comp.complex.function*comp.amount*sum(comp_funcs)
    for i in xrange(gv.num_chemicals):
        #If the organism isn't benefiting, it's 0 complexity
        if comp_vec[i] > 0 and org.function[i] > 1: 
            #otherwise the formula fails for some cases
            comp_vec[i] = comp_vec[i]/org.function[i]
            irr_comp_vec[i] = irr_comp_vec[i]/org.function[i]
        else:
            comp_vec[i] = 0
            irr_comp_vec[i] = 0
            

    complexity = sum(comp_vec)/gv.num_chemicals
    irreducible_complexity = sum(irr_comp_vec)/gv.num_chemicals
    return complexity, irreducible_complexity
    
def breakdown(all_data):
    """
    Breaks down a multi-generation data array and computes the min, lower Q, 
    avg, upper Q, and max for each variable for each generation.
    """
    min = np.amin(all_data,axis = 0)
    avg = np.average(all_data, axis = 0)
    max = np.amax(all_data, axis = 0)
    lower = np.empty_like(avg)
    upper = np.empty_like(avg)
    num = len(all_data)
    fuzzy_index = (num-1)*percentile
    index = int(fuzzy_index)
    offset =  fuzzy_index - index
    all_data = array(all_data)
    #one data point per generation
    if avg.ndim == 1:
        for i in range(len(all_data[0])):
            arr = np.sort(all_data[:,i])
            lower[i] = (1-offset) * arr[index] + (offset)*arr[index+1]
            upper[i] = (1-offset) * arr[-index-1] + (offset)*arr[-index-2]
    #multiple data points per generation
    else:
        for i in range(len(all_data[0])):
            arr = np.sort(all_data[:,i,:],axis = 0)
            lower[i] = (1-offset) * arr[index,:] + (offset)*arr[index+1,:]
            upper[i] = (1-offset) * arr[-index-1,:] + (offset)*arr[-index-2,:]
    return min, lower, avg, upper, max

def breakdown_points(points):
    """
    Computes and returns min, lower Q, avg, upper Q, max of an array of points
    """
    if len(points) == 1:
        return points, points, points, points, points
    min = np.amin(points)
    avg = np.average(points)
    max = np.amax(points)
    fuzzy_index = (len(points)-1)*percentile
    index = int(fuzzy_index)
    offset =  fuzzy_index - index
    arr = np.sort(points)
    lower = (1-offset) * arr[index] + (offset)*arr[index+1]
    upper = (1-offset) * arr[-index-1] + (offset)*arr[-index-2]
    return min, lower, avg, upper, max
