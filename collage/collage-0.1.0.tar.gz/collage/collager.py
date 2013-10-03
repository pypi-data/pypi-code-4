import os
import sys
import numpy
from PIL import Image
from collage.base import CollageObject
from multiprocessing import cpu_count

class Collager(CollageObject):
    """Makes collages using images saved on disk.
    """

    limit_collages = 50
    limit_ranking = 100
    limit_thumbs = 300

    num_workers = cpu_count() * 2

    def __init__(self, path):
        super(Collager, self).__init__(path)
        self.start_queue()
        if self.get_paths('.std'):
            self.make_thumbnails()
            self.select_thumbnails()
            self.render_collages()
        else:
            raise Exception, "No images to collage."

    def make_thumbnails(self):
        """Resize images to tile size.

        Reduces images to the tile size and to the comparison size.
        """
        paths = self.get_paths('.std')[:self.limit_thumbs]
        self.write("Making %s %sx%s replacement tiles" % (
            len(paths), self.tile_size[0], self.tile_size[1]))
        self.thumbnails = []
        for path in paths:
            image = self.open_image(path)
            if image == None:
                self.info("")
                self.info("")
                msg = "Corrupt or empty image file: %s\n" % path
                msg += "Please empty the collage data folders and try again."
                self.exit(msg)
            thumbnail = self.thumbnail(image, self.tile_size)
            self.thumbnails.append(thumbnail)
            self.write('.')
        self.thumbnail_vectors = self.vectorise(self.thumbnails)
        self.write("\n")

    def select_thumbnails(self):
        """Select thumbnails that best cover each image.

        Picks replacement tiles by calculating the closest
        match. Measures the quality of the coverage. Ranks
        images by colourfulness and quality of coverage.
        """
        paths = self.get_paths('.std')[:self.limit_ranking]
        boxes = self.get_boxes()
        msg = "Picking %s replacement tiles " % len(boxes)
        msg += "using %sx%s comparison for " % self.cmp_size
        msg += "each of %s " % len(paths)
        msg += "%sx%s candidate collages" % self.std_size
        self.write(msg)
        self.match_results = {}
        # Add image paths to the task queue.
        for path in paths:
            self.q.put(path)
        # Wait for all images to be processed.
        self.q.join()
        self.write('\n')
        # List results in the original order of the images.
        self.images_tile_indexes = []
        images_fits = []
        colors = []
        for path in paths:
            result = self.match_results[path]
            self.images_tile_indexes.append(result['tile_indexes'])
            images_fits.append(result['fits'])
            colors.append(result['color'])
        # Rank results by color range and fit.
        msg = "Ranking %s collages by color range and tile match quality"
        self.info(msg % len(images_fits))
        fits = zip(images_fits, range(len(images_fits)))
        fits.sort()
        fits_ranks = zip([f[1] for f in fits], range(len(fits)))
        fits_ranks.sort()

        colors = zip(colors, range(len(colors)))
        colors.sort(reverse=True)
        colors_ranks = zip([c[1] for c in colors], range(len(colors)))
        colors_ranks.sort()

        ranks = [(fits_ranks[i][1]+colors_ranks[i][1], fits_ranks[i][0]) for i in range(len(fits_ranks))]
        ranks.sort()
        self.best_for_collages = [r[1] for r in ranks[:self.limit_collages]]

    def do_task(self, path):
        """Select best matching tiles for image in given file path.
        """
        result = {}
        # Load the full image.
        image = self.open_image(path)
        # Count the number colors.
        color = image.convert(
            "P", palette=Image.ADAPTIVE, colors=256
        ).getcolors(maxcolors=256)
        result['color'] = color
        boxes = self.get_boxes()
        # Crop the image into tiles.
        tiles = [image.crop(b) for b in boxes]
        tile_vectors = self.vectorise(tiles)
        # Calculate distance to each thumbnail for each tile.
        # - add newaxis to so thumbnail_vectors is "stretched" for each tile
        x = self.thumbnail_vectors - tile_vectors[:,numpy.newaxis,:,:]
        x = numpy.sqrt(numpy.sum(x**2, axis=3))
        x = numpy.sum(x, axis=2) / len(boxes)

        # Pick off closest thumbnail for each tile.
        tile_indexes = x.argmin(axis=1)
        result['tile_indexes'] = tile_indexes
        # Measure the quality of the match.
        tile_diffs = x.min(axis=1)
        fit = sum(tile_diffs) / float(len(tile_diffs))
        result['fits'] = fit
        sys.stdout.write(".")
        sys.stdout.flush()
        self.match_results[path] = result

    def render_collages(self):
        """Make new images using the best matching tiles."""
        msg = "Rendering best %s collages" % len(self.best_for_collages)
        self.info(msg)
        boxes = self.get_boxes()
        paths = self.get_paths('.std')
        collages = []
        self.collage_paths = []
        for image_index in self.best_for_collages:
            collage = self.new_image()
            tile_indexes = self.images_tile_indexes[image_index]
            for j,k in enumerate(tile_indexes):
                box = boxes[j]
                try:
                    collage.paste(self.thumbnails[k], box)
                except Exception, e:
                    self.error("Couldn't paste thumbnail size %s into box %s on image size %s: %s" % (thumbnail.size, box, collage.size, e))
                    collage = None
                    break
            if collage:
                image_id = os.path.basename(paths[image_index])
                path = self.get_collage_image_path(image_id)
                collage.save(path, format="JPEG")
                self.collage_paths.append(path)
        if self.collage_paths:
            dirname = os.path.dirname(self.collage_paths[0])
            self.info("Collages are saved in: %s" % dirname)

    def get_boxes(self):
        """Construct list of coordinates of tiles on image.
        """
        if not hasattr(self, '_boxes'):
            w,h = self.std_size
            tw,th = self.tile_size
            boxes = []
            for i in range(0,w,tw):
                for j in range(0,h,th):
                    boxes.append((i, j, i+tw, j+th))
            self._boxes = boxes
        return self._boxes

    def vectorise(self, images):
        """Get pixels for image reduced to comparison size.
        """
        v = [self.pixels(self.thumbnail(i, self.cmp_size)) for i in images]
        v = numpy.array(v)
        return v

        # The Lab transformation seems to make things worse?
        shape = v.shape
        v = v.reshape(shape[0]*shape[1], shape[2])
        v = self.rgb2lab(v)
        v = v.reshape(shape)
        return v


    def rgb2lab(self, rgb):
        """"Convert RGB to Lab colorspace.
        """
        rgb = rgb / 255.0   # RGB from 0 to 255. 
        # http://en.wikipedia.org/wiki/SRGB_color_space#The_reverse_transformation
        a = 0.055
        rgb = numpy.choose(rgb > 0.04045, (((rgb+a)/(1.0+a))**2.4, rgb/12.92))
        rgb = rgb * 100
        # Illuminant = D65.
        t1 = numpy.matrix([[0.4124, 0.2126, 0.0193],
                           [0.3576, 0.7152, 0.1192],
                           [0.1805, 0.0722, 0.9505]])
        xyz = numpy.matrix(rgb) * t1
        xyz = numpy.array(xyz)

        xyz = xyz / numpy.array([95.047, 100.0, 108.883])

        # XYZ -> Lab transformation.
        # http://en.wikipedia.org/wiki/Lab_color_space#Forward_transformation
        xyz = numpy.choose(xyz > 0.008856, ( xyz**(1/3), ( 7.787 * xyz) + ( 16 / 116 )))
        t2 = numpy.matrix([[0, 500, 0],
                           [116, -500, 200],
                           [0, 0, -200]])
        lab = numpy.matrix(xyz) * t2
        lab = numpy.array(lab)
        lab = lab - [16, 0, 0]
        lab = numpy.round(lab, 4)
        return lab

 
