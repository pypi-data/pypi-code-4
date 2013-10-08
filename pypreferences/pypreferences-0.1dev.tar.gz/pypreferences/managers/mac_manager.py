from file_manager import FileManager
import os
import errno

class MacManager(FileManager):
   
    def mkdirs_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
 
    def get_path(self, namespace):
        path = os.path.expanduser("~/Library/Preferences/")
        self.mkdirs_p(path)
        filename = "com.bmarty.pypreferences.%s.pref" % namespace
        path = os.path.join(path, filename)
        return path

