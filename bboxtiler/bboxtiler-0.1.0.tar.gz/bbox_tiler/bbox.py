"""This module can be imported or run from the command line to "tile"
a bounding region into a list of bounding boxes."""

import math
import csv
import argparse
import copy

HEADER = ["x", "y", "bbox"]
TILE_DEFAULT = 10

def bounding_pts(x, y, d):
    """Create bounding box list."""

    bb = [[x - d, y + d],
    [x + d, y + d],
    [x + d, y - d],
    [x - d, y - d],
    [x - d, y + d]]

    return bb

def bb_ccw(bb):
    bb.reverse()
    return bb

def get_dx(upper_left, lower_right):
    """Get horizontal distance from 'upper_left' to 'lower_right'."""
    return abs(lower_right[0] - upper_left[0])

def get_dy(upper_left, lower_right):
    """Get vertical distance from 'upper_left' to 'lower_right'."""
    return abs(lower_right[1] - upper_left[1])

def get_x_tiles(upper_left, lower_right, d):
    """Get count of tiles along horizontal axis."""
    return int(math.ceil(get_dx(upper_left, lower_right) / (2 * d)))

def get_y_tiles(upper_left, lower_right, d):
    """Get count of tiles along vertical axis."""
    return int(math.ceil(get_dy(upper_left, lower_right) / (2 * d)))

def calc_d(upper_left, lower_right, n, length):
    """Calculate the distance from the tile centroid to tile edge directly
    to the left or right, or directly above or below the centroid.

    If 'l' (length of tile side) is supplied, just divide it by two to get 'd'.
    Otherwise, do the math to figure out 'd'."""

    if length:
        return length / 2.

    else:
        dx = get_dx(upper_left, lower_right)
        dy = get_dy(upper_left, lower_right)

        return math.sqrt(((dx * dy) / (4. * n)))

def get_y(xy, d, yi):
    """Given xy tuple (likely the upper left corner of a bounding box),
    distance d and tile index yi, return the y coordinate of the tile
    centroid."""
    length = d * 2
    return xy[1] - (length * yi) - d

def get_x(xy, d, xi):
    """Given xy tuple (likely the upper left corner of a bounding box),
    distance d and tile index xi, return the x coordinate of the tile
    centroid."""
    length = d * 2
    return xy[0] + (length * xi) + d

def write_csv(fname, fields_list, data, sep="\t"):
    """Write a text file of tile coordinates and bounding coordinates.
    Defaults to tab separator."""

    with open(fname, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=sep)

        writer.writerow(fields_list)
        for d in data:
            writer.writerow(d)

    return True

def mk_tile_bounding_points(upper_left, lower_right,
                            n=TILE_DEFAULT, length=None, tile_idxs=False):
    """Generate list of x,y coordinates defining a bounding linear ring
    for all tiles in the region defined by the coordinates in
    'upper_left' and 'lower_right'. Tile size and number is determined either
    by a desired approx.  number of tiles (default), or a supplied
    length 'l' of the side of a tile in the coordinate system given in
    'upper_left' and 'lower_right'.

    Returns a list of lists, where each list contains the x and y
    indices for the given tile as well as a list of lists containing
    the points defining a bounding linear ring."""
    data = []

    d = calc_d(upper_left, lower_right, n, length)

    for xi in range(get_x_tiles(upper_left, lower_right, d)):
        for yi in range(get_y_tiles(upper_left, lower_right, d)):

            # calculate x & y of tile centroid
            x = get_x(upper_left, d, xi)
            y = get_y(upper_left, d, yi)

            # calculate tile bounding box based on centroid
            # coordinates and distance to edge
            # bounding box is ordered counter-clockwise
            bb = bb_ccw(bounding_pts(x, y, d))

            # store tile bounding box and (possibly) tile indices as list of lists
            if tile_idxs:
                data.append([xi, yi, bb])
            else:
                data.append(bb)

    return data

def parse_coord_string(s):
    """Parse latlon string of form 'x,y', creating a list of
    form [float(x), float(y)]."""
    return [float(num) for num in s.split(",")]

def parse_args():
    """Parse command line options."""
    parser = argparse.ArgumentParser(description='Generate tile bounding boxes.')
    parser.add_argument("upper_left", metavar="upper-left", help="'x,y' string (comma separated) of upper-left corner of bounding rectangle.")
    parser.add_argument("lower_right", metavar="lower-right", help="'x,y' string (comma separated) of lower-right corner of bounding rectangle.")
    parser.add_argument("-n", "--tile_count", metavar="tile-count", type=int, help="Approximate number of tiles to generate. Defaults to %s" % TILE_DEFAULT)
    parser.add_argument("-l", "--tile-edge-length", type=float, help="Length of tile edge, in the same units as upper-left and upper-right arguments (e.g. degrees or meters)")
    parser.add_argument("-f", "--output-file", metavar="output-file", dest="output_file", help="Output results to tab-separated file at this location.")
    parser.add_argument("-i", "--tile-idxs", dest="tile_idxs", action="store_true", help="Include tile indices in output.")

    args = parser.parse_args()

    upper_left = parse_coord_string(args.upper_left)
    lower_right = parse_coord_string(args.lower_right)
    n = args.tile_count
    length = args.tile_edge_length
    output_file = args.output_file
    tile_idxs = args.tile_idxs

    return upper_left, lower_right, n, length, output_file, tile_idxs

def main():
    upper_left, lower_right, n, length, output_file, tile_idxs = parse_args()
    data = mk_tile_bounding_points(upper_left, lower_right, n, length, tile_idxs)

    if not tile_idxs:
        data = [[d] for d in data]
        HEADER_OUT = [HEADER[-1]]

    # write to disk
    if output_file:
        write_csv(output_file, HEADER_OUT, data)

    # or print everything
    else:
        for line in data:
            print "\t".join(map(str, line))

if __name__ == "__main__":
    main()
