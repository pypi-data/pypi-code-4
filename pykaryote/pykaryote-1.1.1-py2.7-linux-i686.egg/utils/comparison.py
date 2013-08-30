"""
The comparer module is responsible for analyzing the effects of 
changing a variable. It takes care of running the simulations, 
compiling the data, and producing graphs.
"""
import numpy as np
import shutil
import os
import os.path
import glob
import math
import ConfigParser as configparser
import warnings
import pkg_resources
#graphing
import matplotlib.pyplot as plt

from pykaryote.sim.environment import Environment
import pykaryote.utils.environment_draw as environment_draw
import pykaryote.utils.analysis as analysis
from pykaryote.sim.simulation import Simulation
from pykaryote.utils.globals import settings as gv

# ignore warnings about empty data files
warnings.filterwarnings('ignore', r'.*Empty input file.*')

# TODO: refactor metric settings into a config file
metrics_one_col =  ["complexity_avg", "irreducible_complexity_avg", 
"genome_length_avg", "fitness_avg", "1ancestors", "3ancestors", "10ancestors", 
"failed_builds", "gen_time"]
metrics_each_col = ["num_families_current_functional", 
"num_complexes_current_functional", "num_families_ever", "num_complexes_ever",
 "chemicals", "complexes", "percent_functional"]
metrics_logy = ['fitness','chemicals']
# metrics to plot bar graphs of the final values
# must be a list of values from metrics_one_col
metrics_to_plot_final_values = ['genome_length_avg', 'complexity_avg']

def get_config(filename):
    """Reads a comparison configuration file.

    Args:
        filename: The filename of comparison configuration file.

    Returns a tuple of (tuple of option names, list of tuples of values to use)
    
    If a line begins with a ``(``, it is simply ``eval``-ed. (options should 
        have quotes!)
    If the first line doesn't begin with a ``(``, then the text is surrounded 
        by quotes and put in a tuple.
    If subsequent lines don't begin with a ``(``, then they are simply 
        placed into tuples.
    """
    # TODO: rewrite cmp.cfg files to use json instead of eval
    lines = [l.strip() for l in open(filename)] #remove trailing newlines
    if lines[0][0]!='(':
        options = (lines[0],)
    else:
        options = eval(lines[0])
    values = []
    for l in lines[1:]:
         if len(l)>0:
            if l[0]!='(':
                values.append((eval(l),))
            else:
                values.append(eval(l))
    return options, values

def make_cfg(options, replacement_values, base_config, out_filename):
    """Create a sim config file by replacing options in base_config.

    Replaces options in base_config with values from replacement_values and
    saves the resulting simulation configuration file to out_filename.

    Used to create a sim.cfg config file from a cmp.cfg comparison config.
    """
    def replace_value(config, master_config, option, value):
        """Replaces a value in a configuration file.

        Checks to make sure the option exists either in the file,
        or in the master config file.
        """
        for section in config.sections():
            if config.has_option(section, option):
                config.set(section, option, value)
                return
        # option not found in config file
        # see if it is in master config file
        for section in master_config.sections():
            if master_config.has_option(section, option):
                try:
                    config.set(section, option, value)
                except configparser.NoSectionError:
                    config.add_section(section)
                    config.set(section, option, value)
                return
        # option not found in master config file
        raise ValueError('Unknown configuration option: {}'.format(option))

    # read in config file
    config = configparser.RawConfigParser()
    with open(base_config, 'r') as in_file:
        config.readfp(in_file, base_config)
    # read in master config file
    master_config = configparser.RawConfigParser()
    with pkg_resources.resource_stream('pykaryote',
                        os.path.join('configs', 'master.cfg')) as master_file:
        master_config.readfp(master_file)
    # replace values
    for option, value in zip(options, replacement_values):
        replace_value(config, master_config, option, value)
    # write output
    with open(out_filename, 'w') as out_file:
        config.write(out_file)

def get_metrics_files(folder, metric):
    """
    Gets the list of files associated with metric.
    
    *Args*:
        ``folder`` (str): the path to the "comparative-analyzer" folder. *Must* have a trailing '/'.
        ``metric`` (str): the name of the metric.
    
    *Returns* [str..]: the filenames that match.
    """
    files=[]
    i=1
    while os.path.isfile(os.path.join(folder, '%s-%s' % (metric, i))):
        files.append("%s-%i"%(metric,i))
        i+=1
    return files

class Comparer(object):
    """
    Runs a bunch of simulations with slight differences and aggregates the results.
    
    *Args*:
        ``sim_config`` (str) the template configuration file for the experiment
        
        ``cmp_config`` (str) the comparison configuration file for the experiment
        
        ``name`` (str): the name of the comparison; defaults to ``Experiment``
        
        ``data`` (str): the data directory; defaults to the current directory.
        
        ``identical_genomes`` (bool): whether all of the trials simulations 
        should start out with the same set of genomes (identical generation 0)
    """
    def __init__(self, sim_config, cmp_config, name="Experiment", 
                 data='.', clear=True, identical_genomes=True):
        self.vary_attrs,self.values = get_config(cmp_config)
        self.name = name
        self.identical_genomes = identical_genomes
        self.data = data
        self._sim_config = sim_config

        if clear:
            shutil.rmtree(os.path.join(self.data, name), ignore_errors=True)
        os.makedirs(os.path.join(self.data, name))

        #copy the comparison configuration into this comparison's own folder
        shutil.copy(cmp_config, os.path.join(self.data, name))

        #create configuration files for each varied option
        for x, vals in enumerate(self.values):
            out_filename = os.path.join(self.data, name, 'sim-%s.cfg' % x)
            make_cfg(self.vary_attrs, vals, sim_config, out_filename)
    
    def run(self, verbose=True):
        """
        
        *Args*:
            ``verbose``
        """
        #runs sims
        for i in range(len(self.values)):
            name = "sim-%s"%i
            if verbose:
                print "Simulating %s with %s=%s"%(name,self.vary_attrs,self.values[i])
            sim = Simulation(os.path.join(self.data, self.name,
                             'sim-%s.cfg' % i),
                            name=name, 
                            data=os.path.join(self.data, self.name),
                            comparison=True)
            if self.identical_genomes:
                if i==0: #this is the master simulation, all others will borrow its genomes
                    self.master_genomes = [o.genome for o in sim.organisms]
                else:
                    for o in range(len(sim.organisms)):
                        for b in range(len(sim.organisms[o].genome)):
                            sim.organisms[o].genome[b]=self.master_genomes[o][b]
            sim.run(verbose=verbose, log=True)
        #compile data
        agg = AnalyzerAggregator(self.data, self.name, self.values, 
                                 sim_config=self._sim_config)
        agg.compile_all()


class AnalyzerAggregator(object):
    """Aggregates data from multiple simulations into a comparative-analyzer
    directory.
    
    When a comparison is run, it creates an ``analyzer`` directory for each
    type of simulation. ``AnalyzerAggregator`` combines them by putting the
    columns next to each other. For example, combining three simulations, each
    with one column of data, produces a data file with three columns - one for
    each simulation.
    """
    def __init__(self, data_dir, comparison_name, cmp_values, sim_config):
        """
        Args:
            data_dir (str): path to a directory which holds comparisons.
            comparison_name (str): the name of this comparison
            cmp_values: a list of values, one for each type of simulation
                in the comparison.
            sim_config: path to the base simulaiton configuration file.
                Used to load settings for creating threshold graphs.
                (eg: gens_until_complexity_5)
        """
        self.data = data_dir
        self.name = comparison_name
        self.values = cmp_values
        # sim_config is used to load setting for which types of threshold metric
        # graphs to make
        self._sim_config = sim_config
        
    def compile_all(self):
        "Compiles all data files into a single ``comparative-analyzer`` dir."
        try:
            os.makedirs(os.path.join(self.data, self.name, 
                        'comparative-analyzer'))
        except:
            pass
        for m in metrics_one_col:
            self.compile_metric(m, 'one_col')
        for m in metrics_each_col:
            self.compile_metric(m, 'each_col')
        # compile threshold metrics
        if self._sim_config is not None:
            gv.init_globals(self._sim_config)
            for m in gv.metrics:
                name = 'gens_until_{}'.format(m)
                try:
                    # load previously calculated values from multiple runs
                    self.compile_metric('{}.stddev'.format(name), 'one_col')
                    self.compile_metric('{}.blanks'.format(name), 'one_col')
                    self.compile_metric(name, 'one_col')
                    self.compile_metric('num_runs', 'one_col')
                except IOError:
                    # single run
                    self._compile_threshold(name)
        # copy movement data
        self._compile_time_spent_in_gaussian()

    def _compile_time_spent_in_gaussian(self):
        """Copy ``time_spent_in_gaussian`` data to a comparative-analyzer dir.

        This data is used to look at movement. It tracks how long each organism
        spent in each chemical mound (gaussian).

        Subfolders are created inside of 'comparative-analyzer' for each
        simulation. Data files are copied to those subfolders.

        The data files themselves are three dimensional .np files. Each file
        is an array of 2d arrays, one for each run of a batch.
        """
        # copy data files
        for i in range(len(self.values)):
            analyzer_dir = os.path.join(self.data, self.name,
                                        'sim-{}'.format(i), 'analyzer')
            out_dir = os.path.join(self.data, self.name,
                                   'comparative-analyzer',
                                   'sim-{}'.format(i))
            try:
                os.makedirs(out_dir)
            except OSError:
                # directory already exists
                pass
            for data_file in glob.glob(os.path.join(
                                       analyzer_dir,
                                       'time_spent_in_gaussian_gen_*')):
                shutil.copy(data_file, out_dir)

    def _compile_threshold(self, metric):
        """Compiles threshold data for comparisons based off of a single run.

        Comparisons which are aggregates of multiple runs will already have
        this data generated for them.
        """
        out_path = os.path.join(self.data, self.name, 'comparative-analyzer',
                                metric)
        means = []
        stddevs = []
        blankss = []
        for i in range(len(self.values)):
            analyzer_dir = os.path.join(self.data, self.name, 
                                        'sim-{}'.format(i), 'analyzer')
            ann = analysis.Analyzer([analyzer_dir])
            mean, stddev, blanks = ann.quick_read(metric, mode='threshold')
            means.append(mean)
            stddevs.append(stddev)
            blankss.append(blanks)

        means = np.array(means)
        stddevs = np.array(stddevs)
        blankss = np.array(blankss)
        np.savetxt('{}.stddev'.format(out_path), stddevs.T)
        np.savetxt('{}.blanks'.format(out_path), blankss.T)
        np.savetxt(out_path, means.T)
        
    def compile_metric(self, metric, read_style):
        """Compile a single type of data file.
        
        *Args*:
            ``metric`` (str): the filename to read and write
            
            ``read_style`` (str): 
            
            * if ``one_col``, then the metric is assumed to have only one column.  
            * if ``each_col``, then each column is treated as its own metric, 
                and they are each written to "<metric_name>-<col#>"
            
        """
        datas = []
        if read_style=='one_col':
            #the lists contained by datas vary in length, including being [].
            for i in range(len(self.values)):
                datas.append(np.loadtxt(os.path.join(self.data, self.name, 
                                 'sim-%s' % i, 'analyzer', metric), 
                                dtype=float))
                if datas[-1].shape == (): #get at least one dimension.
                    datas[-1] = np.array([datas[-1]], dtype=float)
            num_rows = [val.shape[0] for val in datas] #for each val
            # TODO: use np.savetxt here
            f = open(os.path.join(self.data, self.name, 'comparative-analyzer', 
                     metric), 'w')
            for row in range(max(num_rows)):
                for val in range(len(datas)):
                    if row < num_rows[val]: #there's a value; write it.
                        f.write("%3.4f "%datas[val][row])
                    else: # -1 is used when the data file is empty
                        f.write("-1 ")
                f.write("\n")
            f.close()
        elif read_style=='each_col': 
            #the lists contained by datas vary in length, but are never []. the lists contained by those don't vary in length for now.
            for i in range(len(self.values)):
                datas.append(np.loadtxt(os.path.join(self.data, self.name, 
                                 'sim-%s' % i, 'analyzer', metric), 
                                dtype=float, ndmin=2))
            num_cols = [val.shape[1] for val in datas]
            num_rows = [val.shape[0] for val in datas]
            for col in range(max(num_cols)): #each column becomes a file
                f = open(os.path.join(self.data, self.name, 
                         'comparative-analyzer', '%s-%s' % (metric, 1 + col)),
                        'w')
                for row in range(max(num_rows)):
                    for val in range(len(datas)):
                        if row < num_rows[val] and col < num_cols[val]:
                            f.write("%3.4f "%datas[val][row][col])
                        else:
                            # -1 is used when there is no more data in the file
                            f.write('-1 ')
                    f.write('\n')
                f.close()
        else:
            raise Exception("unrecognized read_style: %s"%read_style)


class Grapher(object):
    """
    Takes a comparison's analyzer directory and provides methods for 
    plotting the data.
    
    *Args*:
        ``data_folder`` (str): a folder which contains a folder 
        named ``comparative-analyzer``, which has the necessary data.
    """
    # TODO: pass thresholds as a 'gens_until_complexity_avg.thresholds' file
        # so that way sim_config does not need to be passed to Grapher
    def __init__(self, data_folder, sim_config, cmp_config_filename=None,
                 verbose=True):
        gv.init_globals(sim_config)
        self.base = data_folder
        if self.base[-1]!='/': self.base+='/'
        if cmp_config_filename is None:
            cmp_config_filename = os.path.join(self.base, 'cmp.cfg')
        self.vary_attrs, self.values = get_config(cmp_config_filename)
        # load the number of simulations run for each varied attribute
        try:
            num_runs = np.loadtxt(os.path.join(self.base,
                                  "comparative-analyzer", 'num_runs'), 
                                  dtype=float, ndmin=1)
            if min(num_runs) == max(num_runs):
                self.num_runs = '{}'.format(int(num_runs[0]))
            else:
                self.num_runs = '{} to {}'.format(int(min(num_runs)),
                                                  int(max(num_runs)))
        except IOError:
            self.num_runs = '1'
        self._verbose = verbose

    def _report_status(self, string):
        """If verbose output is enabled, prints a string to stdout.
        """
        if self._verbose:
            print string
        
    def save_all(self):
        "Saves images of the plots of all of the metrics"
        try: 
            os.makedirs(os.path.join(self.base, 'graphs'))
        except:
            pass
        for m in metrics_one_col:
            plt.figure()
            self.plot(m)
            plt.savefig(os.path.join(self.base, 'graphs', '%s.png' % m))
        for m in metrics_each_col:
            for f in get_metrics_files(os.path.join(self.base, 
                                       'comparative-analyzer'), m):
                plt.figure()
                self.plot(f)
                plt.savefig(os.path.join(self.base, 'graphs', '%s.png' % f))
        for m in metrics_to_plot_final_values:
            plt.figure()
            self.plot_final_values(m)
            plt.savefig(os.path.join(self.base, 'graphs', 
                        '%s-final-values.png' % m))
        for metric, values in zip(gv.metrics, gv.thresholds):
            ann_dir = os.path.join(self.base, 'comparative-analyzer')
            self.plot_threshold(metric, values, save_dir=ann_dir)
        self.draw_environment(save_dir=os.path.join(self.base, 'graphs'))
        self.save_time_spent_in_gaussian()
        
    def plot(self, metric):
        """
        
        *Args*:
            ``metric`` (str): the name of the file to be plotted, 
            inside of the directory "comparative-analyzer". 
            Columns must correspond to values of vary_attr and 
            rows to generations.
        """
        self._report_status('plotting %s' % metric)
        logy = sum([m in metric for m in metrics_logy]) > 0
        try:
            data = np.loadtxt(os.path.join(self.base, "comparative-analyzer",
                        metric), dtype=float, ndmin=2) #row=generation
        except IOError:
            print 'no data found in', metric, 'a'

        plt.axes([.1,.1,.65,.8])
        if logy and not any(row[0]>0 for row in data): #hack to allow logy even when all values are zero
            for x in data[len(data)/2]:
                if x>0:
                    plt.plot([x])
                    break
            else:
                plt.plot([1e-1])
        f=(plt.semilogy if logy else plt.plot)
        for c in range(data.shape[1]): #each column
            amount_done= 1.0 - float(c) / data.shape[1]
            f(
                data[:,c],
                linewidth=amount_done*2+.5,
                color=(.3-.3*amount_done,1-amount_done,.3*amount_done),
                label=str(self.values[c]),
                linestyle=["solid","dashed","dashdot","dotted"][c % 4]
            )
        plt.title("%s over %s runs" % (metric, self.num_runs))
        plt.xlabel("generation")
        plt.ylabel(metric)
        plt.legend(title=self.vary_attrs, bbox_to_anchor=(1.01 ,1.), 
                   loc=2, borderaxespad=0.)

    def plot_final_values(self, metric):
        """Plots a bar graph of the final values of a metric.

        Each var_attr is a bar on the x axis.
        metric is the y axis.
        The value of each bar is the value of metric at the last generation.

        Input files contain 2d numpy arrays containing values for metric, where
        each row is a generation and each column corresponds to a value 
        of self.vary_attrs.

        For example:
            x-axis (bars) = varying config parameter
                (ex: cost of genome length)
            y-axis = final value for a metric after 1000 runs 
                (ex: average complexity)

        Args:
            metric (str): The metric to plot.
        """
        self._report_status("plotting final values of %s" % metric)
        try:
            data = np.genfromtxt(os.path.join(self.base, "comparative-analyzer",
                metric), dtype=float) #row=generation
        except IOError:
            print 'no data found in', metric
            return
        # ensure data is a 2d array
        if len(data.shape) < 2:
            if len(self.values) == 1:
                # there is only one column
                # this happens when only one value is changed in sim.cfg
                data.resize(data.shape[0], 1)
            else:
                # there is only one row
                # this happens when only one generation is run
                data.resize(1, data.shape[0])
        # check if the file is empty (no data to graph)
        if data.shape[1] == 0:
            print 'data file for metric', metric, 'is empty'
            return
        num_bars = data.shape[1] # number of columns
        num_generations = data.shape[0] # number of rows
        bar_x_cords = np.arange(num_bars) # x locations for the bars
        metrics_at_final_generation = data[-1] # heights of the bars
        width = 0.2
        bar_labels = self.values
        p1 = plt.bar(bar_x_cords, metrics_at_final_generation, width,
                     color='#175EC8')
        plt.ylabel(metric)
        plt.xlabel(self.vary_attrs)
        plt.title('%s after %d generations over %s runs' % (metric, 
                  num_generations, self.num_runs))
        plt.xticks(bar_x_cords+width/2.0, bar_labels)

    def plot_threshold(self, metric, thresholds, save_dir=None):
        """Plots a scatter plot of the number of generations it took a metric
        to pass a threshold value.

        These graphs are specified in the 'threshold-metrics' section of 
        a simulation's configuration file.
        """
        def new_plot(save_dir=save_dir, window_title=self.base):
            if save_dir is not None:
                plt.figure()

        def end_plot(name, save_dir=save_dir):
            if save_dir is not None:
                plt.savefig(os.path.join(self.base, 'graphs',
                            '{}.png'.format(name)))

        self._report_status("plotting threshold gens of %s" % metric)

        dir_path = os.path.join(self.base, 'comparative-analyzer')
        data_fname = 'gens_until_{}'.format(metric)
        stddev_fname = '{}.stddev'.format(data_fname)
        blanks_fname = '{}.blanks'.format(data_fname)
        data = np.loadtxt(os.path.join(dir_path, data_fname), ndmin=2)
        stddev = np.loadtxt(os.path.join(dir_path, stddev_fname), ndmin=2)
        blanks = np.loadtxt(os.path.join(dir_path, blanks_fname), ndmin=2)
        # calculate the fraction of runs which did not reach the threshold
        try:
            num_runs = np.loadtxt(os.path.join(self.base,
                                  "comparative-analyzer", 'num_runs'),
                                  dtype=float, ndmin=1)
        except IOError:
            num_runs = np.ones(blanks.shape[1])
        percent_blanks = np.empty(blanks.shape)
        for col_num, col in enumerate(blanks.T):
            for i in range(len(col)):
                percent_blanks[i, col_num] = col[i] / num_runs[col_num]

        # graph each threshold which was recorded for this metric
        for threshold_index, threshold in enumerate(thresholds):
            # plot blanks graphs
            new_plot()
            num_bars = data.shape[1]
            num_options = data.shape[0]
            bar_x_cords = np.arange(num_bars)
            percent_blanks_this_threshold = percent_blanks[threshold_index]
            width = 0.2
            bar_labels = self.values
            threshold = thresholds[threshold_index]
            plt.ylim(0.0, 1.0)
            p1 = plt.bar(bar_x_cords, percent_blanks_this_threshold, width,
                         color='#175EC8')
            plt.ylabel('percent runs')
            plt.xlabel(self.vary_attrs)
            plt.title('percent runs which did not reach '\
                      '{} {} over {} runs'.format(metric, threshold,
                                                 self.num_runs))
            plt.xticks(bar_x_cords + width / 2.0, bar_labels)
            plt.subplots_adjust(bottom=0.10)
            end_plot('percent_not_passed_{}_{}'.format(metric, threshold))

            # plot gens_until graphs
            new_plot()
            # when blank runs appear in the middle 80%, draw the bar red
            # this way data with blanks in it are drawn in red to indicate
            # that the average is wrong
            failed_threshold = (1.0 - gv.mean_to_aggregate) / 2.0
            bad_mask = blanks[threshold_index] >= (num_runs *
                                                   failed_threshold).astype(int)
            good_mask = ~bad_mask
            bad_gens_until_threshold = data[threshold_index][bad_mask]
            good_gens_until_threshold = data[threshold_index][good_mask]
            bad_stddev = stddev[threshold_index][bad_mask]
            good_stddev = stddev[threshold_index][good_mask]
            bad_bar_x_cords = bar_x_cords[bad_mask]
            good_bar_x_cords = bar_x_cords[good_mask]
            if len(good_bar_x_cords):
                good = plt.bar(good_bar_x_cords, good_gens_until_threshold,
                               width, yerr=good_stddev, color='#175EC8',
                               ecolor='#0A122A',
                               label='threshold always reached')
            if len(bad_bar_x_cords):
                bad = plt.bar(bad_bar_x_cords, bad_gens_until_threshold, width,
                              yerr=bad_stddev, color='#C60F0F',
                              ecolor='#2A0A0A', label='contains blanks')
            plt.ylabel('generations')
            plt.xlabel(self.vary_attrs)
            plt.title('generations until {} {} over {} runs'.format(metric, 
                      threshold, self.num_runs))
            plt.xticks(bar_x_cords + width / 2.0, bar_labels)
            plt.axis('auto')
            plt.ylim(ymin=0.0)
            plt.subplots_adjust(bottom=0.10)
            leg = plt.legend(loc='best', fancybox=True)
            leg.get_frame().set_alpha(0.5)
            end_plot('gens_until_{}_{}'.format(metric, threshold))

    def draw_environment(self, save_dir):
        """Draws the chemical environment and saves as an image.
        """
        env = Environment((gv.rows, gv.columns), log=False)
        environment_draw.draw_environment(env.grid, os.path.join(
                                        save_dir, 'environment.png'))

    def save_time_spent_in_gaussian(self):
        """Plots ``time_spent_in_gaussian`` data.

        Data should only be present if num_runs == 0.
        Data files are located in folders named
        ``comparative-analyzer/sim-x/``, where ``x`` is a number associated
        with each simulation.
        """
        save_dir=os.path.join(self.base, 'graphs')
        for sim_dir in glob.glob(os.path.join(self.base,
                                 'comparative-analyzer', 'sim-*')):
            ann = analysis.Analyzer([sim_dir])
            ann.plot_time_spent_in_gaussian()
            sim_num = os.path.split(sim_dir)[1][4:]
            plt.savefig(os.path.join(save_dir,
                        'time_spent_in_gaussians_sim_{}'.format(sim_num)))

