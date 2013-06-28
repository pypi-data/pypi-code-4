import fnmatch
import os

from .sass import compile_str

from watchdog.events import FileSystemEventHandler

class FileSystemEvents(FileSystemEventHandler):
    """Handler for all filesystem events."""

    def __init__(self, source_path, dest_path):
        super(FileSystemEvents, self).__init__()

        self._source_path = source_path
        self._dest_path = dest_path

    def get_scss_files(self, skip_partials=True, with_source_path=False):
        """Gets all SCSS files in the source directory.

        :param bool skip_partials: If True, partials will be ignored. Otherwise,
                                   all SCSS files, including ones that begin
                                   with '_' will be returned.
        :param boom with_source_path: If true, the `source_path` will be added
                                      to all of the paths. Otherwise, it will
                                      be stripped.
        :returns: A list of the SCSS files in the source directory

        """
        scss_files = []

        for root, dirs, files in os.walk(self._source_path):
            for filename in fnmatch.filter(files, "*.scss"):
                if filename.startswith("_") and skip_partials:
                    continue

                full_path = os.path.join(root, filename)
                if not with_source_path:
                    full_path = full_path.split(self._source_path)[1]

                    if full_path.startswith("/"):
                        full_path = full_path[1:]

                scss_files.append(full_path)

        return scss_files

    def compile_scss(self):
        if not os.path.exists(self._dest_path):
            os.makedirs(self._dest_path)

        orig_path = os.getcwd()

        for scss_file in self.get_scss_files():
            # Read in the source SCSS file contents
            contents = ""
            with open(os.path.join(self._source_path, scss_file)) as open_file:
                contents = open_file.read()

            # Write out the CSS file
            css_filename = os.path.splitext(scss_file)[0] + ".css"

            with open(os.path.join(self._dest_path, css_filename), 'w') as css_file:
                os.chdir(self._source_path)
                css_file.write(compile_str(contents))
                os.chdir(orig_path)

    def on_any_event(self, event):
        self.compile_scss()
