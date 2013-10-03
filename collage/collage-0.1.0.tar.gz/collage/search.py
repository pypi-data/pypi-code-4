import os
import time
import json
import urllib
import urllib2
from StringIO import StringIO
import numpy
from collage.base import CollageObject

class GoogleImages(CollageObject):
    """Encapsulate the Google Images service.
    """

    num_workers = 12

    def __init__(self, path, max_results=None):
        super(GoogleImages, self).__init__(path)
        self.max_results = max_results or 60

    def is_url_in_history(self, url):
        return os.path.exists(self.get_history_path(self.make_hash(url)))

    def put_url_in_history(self, url):
        path = self.get_history_path(self.make_hash(url))
        try:
            open(path, "w").close()
        except Exception, e:
            self.warn("Unable to put item in history: %s: %s" % (url, e))

    def pull(self, queries):
        """Search for and save images using list of query strings.
        """
        self.start_queue()
        self.results = []
        threads = []
        self.info("Saving images in: %s" % self.path)
        for query in queries:
            self.info("Searching for \"%s\" images..." % query)
            start = 0
            while start < self.max_results:
                api_url = self.make_api_url(query, start)
                if self.is_url_in_history(api_url):
                    self.info("Already have %s" % api_url)
                    start += 4  # Normal number of results.
                    continue
                self.put_url_in_history(api_url)
                data = self.http_get(api_url)
                if data:
                    msg = json.loads(data)
                    if msg['responseStatus'] == 200 and msg['responseData']:
                        # Good response.
                        newresults = msg['responseData']['results']
                        if not len(newresults):
                            self.warn("No results in response: %s" % msg)
                            time.sleep(3)
                            break
                        self.results += newresults
                        start += len(newresults)
                        # Retrieve.
                        for result in newresults:
                            image_url = result['unescapedUrl']
                            image_id = self.make_hash(image_url)
                            image_path = self.get_std_image_path(image_id)
                            if 'dogdrip.net/' in image_url:
                                # Exceptionally slow domain. :-)
                                self.info("Skipping %s" % image_url)
                            if self.is_url_in_history(image_url):
                                # Seen it already.
                                self.info("Already have %s" % image_url)
                            else:
                                # Put URL in history, to avoid repeats.
                                self.put_url_in_history(image_url)
                                # Join queue to retrieve image content.
                                self.q.put(image_url)
                    else:
                        # Bad response.
                        details = msg.get('responseDetails', '')
                        if details.startswith('qps rate exceeded'):
                            self.warn('Google just complained about ' +\
                              'too many queries per second. Pausing...')
                            time.sleep(15)
                        else:
                            self.warn("Response not OK: %s" % msg)
                            time.sleep(3)
                            break
                else:
                    # No data in response.
                    self.warn("No data from %s" % api_url)
                    time.sleep(3)
                    break
                # Be nice to Google.
                time.sleep(1.5)
        # Wait for workers to finish processing the queue.
        self.q.join()
        # Summarise results.
        std_count = len(self.get_paths('.std'))
        if not std_count:
            self.warn("No images found.")
        self.info("There are %d images." % std_count)

    def do_task(self, image_url):
        """Retrieve and process image into standard size and category."""
        raw_image_data = self.http_get(image_url)
        if raw_image_data:
            image_id = self.make_hash(image_url)
            # Attempt to parse image data into an Image object.
            image = self.open_image(StringIO(raw_image_data))
            if not image:
                return
            # Convert image to RGB, if necessary.
            if image.mode != "RGB":
                try:
                    image = image.convert("RGB")
                except Exception, e:
                    self.warn("Couldn't convert '%s' to RGB %s: %s" % (
                        image.mode, image_url, e))
                    return
            # Resize to standard size.
            image = self.thumbnail(image, self.std_size)
            # Save standard size.
            std_image_path = self.get_std_image_path(image_id)
            try:
                image.save(std_image_path, format='JPEG')
            except Exception, e:
                self.warn("Couldn't save as JPEG %s: %s", (std_image_path, e))
            # Categorise by fixed colors.
            colors = {
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
            }
            names = colors.keys()
            values = numpy.array([colors[n] for n in names])
            pixels = numpy.array(self.pixels(self.thumbnail(image,(100,100))))
            # Calculate Euclidean distances to each color from all pixels.
            # - insert new axis to "stretch" color values across all pixels
            x = values - pixels[:,numpy.newaxis,:]
            x = numpy.sqrt(numpy.sum(x**2, axis=2))
            # Average the distances across all pixels.
            x = numpy.sum(x, axis=0) / len(pixels)
            color_name = names[x.argmin()]

            # Save image by category.
            color_image_path = self.get_color_image_path(image_id, color_name)
            image.save(color_image_path, format='JPEG')

    def make_api_url(self, query, start):
        """Make URL for Google Image API.
        """
        base_url = 'https://ajax.googleapis.com/ajax/services/search/images'
        api_url_args = [('q', query), ('start', start), ('v', '1.0')]
        return base_url + '?' + urllib.urlencode(api_url_args)

    def write_file(self, path, data):
        """Write data to file.
        """
        f = file(path, 'wb')
        try:
            f.write(data)
        except Exception, e:
            self.warn("Unable to write file %s: %s" % (path, e))
        finally:
            f.close()

    def make_hash(self, token):
        """Convert given image URL into unique ID.
        """
        return str(hash(token))

    def http_get(self, url):
        """Retrieve object from the internet.
        """
        try:
            data = self.get_opener().open(url, timeout=10).read()
        except Exception, e:
            self.warn("Unable to get %s: %s" % (url, e))
        else:
            self.info(url)
            return data

    def get_opener(self):
        """Lazy-load the HTTP opener.
        """
        if not hasattr(self, '_opener'):
            self._opener = urllib2.build_opener()
            # Add headers to reduce rejections.
            self._opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        return self._opener

