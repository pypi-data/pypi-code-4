import os
import unittest

from paegan.viz.trajectory import CFTrajectory, save_animation

class TrajectoryTests(unittest.TestCase):
        
    def test_full_animation(self):
        traj = CFTrajectory("/data/animations/68day.nc")
        output_movie = "/data/animations/from_netcdf.avi"
        shore_path = "/data/lm/shore/alaska/New_Land_Clean.shp"
        bathy_path = "/data/lm/bathy/ETOPO1_Bed_g_gmt4.grd"
        status = traj.plot_animate(output_movie, bathy=bathy_path, shore_path=shore_path)
        assert status is True
        
    def test_save_animation(self):
        root_dir = os.path.join(os.path.dirname(__file__), "resources/trajectory_images")
        files = sorted(os.listdir(root_dir))
        files = map(lambda x: os.path.join(root_dir,x),files)
        #print files
        output_movie = "/data/animations/from_files.avi"
        status = save_animation(output_movie, files, clear_temp=False)
        assert status is True