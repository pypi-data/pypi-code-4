"""This package builds collages using images downloaded from
the internet. It makes a set of tiles from the images, which
are matched against the images and used to cover images which match well.

The images which happen to be fitted most closely by the tiles
are rendered with the matching tiles. The resulting images resemble the
original images, but are made up entirely from minature versions of the
same images.

Images are fetched according to a query, optionally provided by the user.

The downloaded images are categoried by primary colour on disk.

Code example
------------

    from collage.main import Application
    Application().query(['face', 'kitten'])

"""

