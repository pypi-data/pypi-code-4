import unittest
import os
import os.path
import shutil
import glob
import tempfile
import ConfigParser as configparser
import matplotlib
matplotlib.use('Agg') # for graphing without an x server
import matplotlib.pyplot as plt
from pkg_resources import resource_filename
from pykaryote.utils.globals import settings as gv
from pykaryote.utils import analysis
from pykaryote.utils import environment_draw
import pykaryote.sim.environment
import pykaryote.sim.simulation
import pykaryote.utils.comparison as comparison

#TODO: add good test coverage for most of the application
#TODO: add tests for petri
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestGlobals(unittest.TestCase):
    def test_init_globals(self):
        """Tests loading of partial sim.cfg files.
        """
        generation_limit = gv.generation_limit
        self.assertEqual(gv.randomseed, 0)
        sim_config = os.path.join(SCRIPT_DIR, 'test_data',
                                  'testInitGlobals-sim.cfg')
        gv.init_globals(sim_config)
        self.assertEqual(gv.randomseed, 999)
        self.assertEqual(gv.generation_limit, generation_limit)

class TestEnvironment(unittest.TestCase):
    """Tests pykaryote.sim.environment.Environment.

    Tests focus on correct creation of the environment grid.
    """
    def setUp(self):
        data_dir = os.path.join(SCRIPT_DIR, 'test_data')
        gv.init_globals(os.path.join(data_dir, 'testEnvironment-sim.cfg'))
        self.env = pykaryote.sim.environment.Environment((gv.rows,
                                                         gv.columns),
        log=False)

    def test_make_flat_grid(self):
        """Tests Environment._make_flat_grid()
        """
        self.env.grid = self.env._make_flat_grid()
        self.assertTrue((self.env.grid == 1.0).all())

    def test_make_gaussian_grid(self):
        """Tests Environment._make_gaussian_grid()
        """
        self.env.grid = self.env._make_gaussian_grid()
        self.assertEqual(self.env.grid[0,0,0], 1.0)
        self.assertTrue(self.env.grid[9,9,0] < 0.0000001)


class TestReadComparison(unittest.TestCase):
    """Tests the comparison.get_config() method, which reads comparison
    configuration files.
    """
    def setUp(self):
        self._base_dir = os.path.join(SCRIPT_DIR, 'test_data')

    def test_get_config(self):
        """Tests comparison.get_config(), which reads a comparison config file.
        """
        options, values = comparison.get_config(os.path.join(self._base_dir,
                                                'get_config_cmp.cfg'))
        self.assertEqual(options, ('test_option',))
        self.assertEqual(values, [(1,), (2,), (3,)])
        options, values = comparison.get_config(os.path.join(self._base_dir,
                                                'get_config_2_cmp.cfg'))
        self.assertEqual(options, ('t1', 't2'))
        self.assertEqual(values, [(1, 2), (3, 4)])


class TestMakeConfig(unittest.TestCase):
    """Tests the comparison.make_cfg() method, which creates config files
    from comparison configuration files.
    """
    def setUp(self):
        self._base_dir = os.path.join(SCRIPT_DIR, 'test_data')
        self._out_filename = os.path.join(self._base_dir,
                                          'temp_made_config.cfg')

    def test_make_config(self):
        """Tests comparison.make_cfg(), which creates config files from
        comparison config files.
        """
        base_config = os.path.join(self._base_dir, 'make_config.cfg')
        comparison.make_cfg(['point_mutate_chance'], [3.14], base_config,
                               self._out_filename)
        config = configparser.RawConfigParser()
        config.read(self._out_filename)
        self.assertTrue(config.has_option('global', 'generation_limit'))
        self.assertTrue(config.has_option('genome', 'point_mutate_chance'))
        self.assertTrue(not config.has_section('organism'))

    def tearDown(self):
        """Delete temporary file.
        """
        try:
            os.remove(self._out_filename)
        except:
            pass


class TestTimeSpentInGaussian(unittest.TestCase):
    """Tests the saving and graphing of data about how long each organism
    spent in each chemical mound/gaussian.
    """
    def setUp(self):
        self.sim_name = 'TestTimeSpentInGaussian'
        self.data_dir = tempfile.mkdtemp(prefix='pykaryote')
        self.test_data_dir = os.path.join(SCRIPT_DIR, 'test_data')
        sim = pykaryote.sim.simulation.Simulation(os.path.join(
                                                  self.test_data_dir,
                            'TestTimeSpentInGaussian-sim.cfg'),
                             name=self.sim_name,
                             data=self.data_dir)
        sim.run(log=False, verbose=False)
        self._analyzer_dir = os.path.join(self.data_dir, self.sim_name,
                                          'analyzer')
        self._ann = analysis.Analyzer([self._analyzer_dir])

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_time_spent_in_gaussian(self):
        """Ensures that the time_spent_in_gaussian data file is correct.

        Checks array dimensions.
        Checks that array sums to gv.generation_length.
        """
        # TODO: add a unit test to test graphing when there is no data to read
        
        for fname in os.listdir(self._analyzer_dir):
            if fname[:27] == 'time_spent_in_gaussian_gen_':
                data = self._ann.quick_read(fname, ndmin=2)
                self.assertEqual(data.shape,
                                 (gv.num_organisms, len(gv.gaussians) + 1))
                for row in data:
                    self.assertEqual(row.sum(), gv.generation_length)

    def test_plot_time_spent_in_gaussian(self):
        """Test the plotting of ``time_spent_in_gaussian`` data.
        """
        self._ann.plot_time_spent_in_gaussian()
        plt.savefig(os.path.join(self.data_dir, 'time_spent_in_gaussians.png'))

    def test_flat_environment(self):
        """Tests plotting with a flat environment.

        Since there are no gaussians, no data should be recorded, and the graph
        should be blank.
        """
        sim_name = 'TestTimeSpentInFlat'
        analyzer_dir = os.path.join(self.data_dir, sim_name, 'analyzer')
        sim = pykaryote.sim.simulation.Simulation(os.path.join(
                                                  self.test_data_dir,
                                                'TestTimeSpentInFlat-sim.cfg'),
                                            name=sim_name, data=self.data_dir)
        sim.run(log=False, verbose=False)
        time_spent_data = [f for f in os.listdir(analyzer_dir)
                            if f[:27] == 'time_spent_in_gaussian_gen_']
        self.assertEqual(time_spent_data, [])
        ann = analysis.Analyzer([analyzer_dir])
        ann.plot_time_spent_in_gaussian()
        plt.savefig(os.path.join(self.data_dir,
                    'time_spent_in_gaussian_flat.png'))
        shutil.rmtree(os.path.join(self.data_dir, sim_name),
                      ignore_errors=True)

    def tearDown(self):
        """Removes simulation data.
        """
        shutil.rmtree(os.path.join(self.data_dir, self.sim_name),
                      ignore_errors=True)

#TODO: test running and analyzing simulations with only one generation.


class TestEnvironmentDraw(unittest.TestCase):
    """Tests pykaryote.utils.environment_draw.
    """
    def setUp(self):
        self.data_dir = os.path.join(SCRIPT_DIR, 'test_data')
        gv.init_globals(os.path.join(self.data_dir,
                        'testEnvironmentDraw-sim.cfg'))
        self.env = pykaryote.sim.environment.Environment((gv.columns,
                                                         gv.rows), log=False)

    def test_draw_environment(self):
        temp_dir = tempfile.mkdtemp(prefix='pykaryote')
        env = pykaryote.sim.environment.Environment((gv.columns, gv.rows),
                                                    log=False)
        filename = os.path.join(temp_dir, 'environment.png')
        environment_draw.draw_environment(env.grid, out_filename=filename)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_make_chemical_colors(self):
        colors = environment_draw.make_chemical_colors(1)
        self.assertEqual(colors, [(191, 64, 64)])
        colors = environment_draw.make_chemical_colors(3)
        expected = [(191, 64, 64), (64, 191, 64), (64, 64, 191)]
        self.assertEqual(colors, expected)


class TestAnalyzerQuickRead(unittest.TestCase):
    """Tests pykaryote.utils.analysis.Analyzer.quick_read()

    Tests are focused on calls where mode='threshold', which is used to
    gather data on how many generations it takes a metric to reach a threshold
    value.

    Test coverage is very minimal.
    """

    def setUp(self):
        base_dir = os.path.join(SCRIPT_DIR, 'test_data', 'analyzer_quick_read')
        gv.init_globals(os.path.join(base_dir, 'sim.cfg'))
        analyzer_dirs = []
        for x in range(12):
            analyzer_dirs.append(os.path.join(base_dir, 'ann{}'.format(x)))
        self.ann = analysis.Analyzer(analyzer_dirs)
        aggregate = self.ann.quick_read('gens_until_complexity_avg',
                                        mode='threshold')
        self.mean = aggregate[0]
        self.stddev = aggregate[1]
        self.blanks = aggregate[2]
        self.complexity = self.ann.quick_read('complexity_avg')

    def test_shape(self):
        """Make sure the resulting data is the right shape.
        """
        self.assertEqual(self.mean.shape, (6,))
        self.assertEqual(self.stddev.shape, (6,))
        self.assertEqual(self.blanks.shape, (6,))
        self.assertEqual(self.complexity.shape, (1000,))
        
    def test_blanks(self):
        """Make sure the right number of blanks is reported.
        """
        self.assertTrue(self.blanks[0] == 0)
        self.assertTrue(self.blanks[1] == 0)
        self.assertTrue(self.blanks[2] == 0)
        self.assertTrue(self.blanks[3] == 0)
        self.assertTrue(self.blanks[4] > 0)
        self.assertTrue(self.blanks[5] == 12)

    def test_complexity(self):
        """Make sure complexity_avg is right.
        """
        self.assertEqual(self.complexity[0], 0.0)
        self.assertTrue(self.complexity[1] != 1.019066099611200043e-03)
        self.assertEqual(self.complexity[999], 3.462880888059239659e+00)

    def test_means(self):
        """Make sure the correct means are reported.
        """
        self.assertTrue(self.mean[5] == 1000.0)

    def test_variable_length_data(self):
        """Test that data with varying length (number of generations) is
        handled correctly.

        For simulations where a time or complexity limit is used instead of
        a generation limit.
        """
        base_dir = os.path.join(SCRIPT_DIR, 'test_data')
        data_folders = glob.glob(os.path.join(base_dir,
                                'analyzer_variable_length', '*', 'analyzer'))
        ann = analysis.Analyzer(data_folders)
        data = ann.quick_read('complexity_avg')
        self.assertEqual(data.shape, (78,))
        data = ann.quick_read('chemical_complexity')

def run():
    """Runs unit tests with a command line interface.
    """
    unittest.main()

if __name__ == '__main__':
    run()
