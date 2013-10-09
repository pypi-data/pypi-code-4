import os
import random
import time
import sys
import wallpyper

usage = """
USAGE: python randomiser.py wallpaper_dir interval
    wallpaper_dir: /absolute/path/to/existing/local/directory
    interval: in seconds between changes
"""

# Process input args
if len(sys.argv) != 3:
	print(usage)
	exit(1)
wallpaper_dir = sys.argv[1]
if (not os.path.isdir(wallpaper_dir)) or (wallpaper_dir[0] != '/'):
	print(usage)
	exit(1)
randomiser_interval = sys.argv[2]
try: randomiser_interval = float(randomiser_interval)
except:
	print(usage)
	exit(1)
if randomiser_interval <= 0:
	print(usage)
	exit(1)

# Get image file paths
paths = []
for dummy1, dummy2, files in os.walk(wallpaper_dir):
	paths = ['%s/%s' % (wallpaper_dir, f) for f in files]
	break

# Randomiser loop
try:
	while True:
		wallpyper.set_wallpaper(random.choice(paths))
		time.sleep(randomiser_interval)
except KeyboardInterrupt as e:
	pass

exit(0)