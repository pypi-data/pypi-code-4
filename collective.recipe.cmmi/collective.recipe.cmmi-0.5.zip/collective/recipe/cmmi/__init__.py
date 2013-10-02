from zc.recipe.cmmi import Recipe as Base
from zc.recipe.cmmi import system
import logging
import os
import tempfile


class Recipe(Base):

    def build(self):
        tmp = None
        if 'patches' in self.options:
            if 'patch' in self.options:
                raise ValueError("Can't use 'patch' and 'patches' together.")
            patch_content = []
            for patch in self.options['patches'].split():
                patch_content.append(open(patch).read())
            tmp = tempfile.mkstemp()
            f = open(tmp[1], 'w')
            f.write('\n'.join(patch_content))
            f.close()
            self.patch = tmp[1]
        try:
            result = Base.build(self)
        finally:
            if tmp:
                os.remove(tmp[1])
        return result

    def cmmi(self, dest):
        """Do the 'configure; make; make install' command sequence.

        When this is called, the current working directory is the
        source directory.  The 'dest' parameter specifies the
        installation prefix.

        This can be overridden by subclasses to support packages whose
        command sequence is different.
        """
        options = self.configure_options
        # Patch check for duplicate --prefix in extra_options
        if options is None and '--prefix' not in self.extra_options:
            options = '--prefix=%s' % dest
        else:
            options = ''
        if self.extra_options:
            options += ' %s' % self.extra_options
        # add logging here
        logger = logging.getLogger(self.name)
        logger.debug("In %s" % os.getcwd())
        logger.debug("%s %s" % (self.configure_cmd, options))
        system("%s %s" % (self.configure_cmd, options))
        # add support for different make_options
        self.make_options = self.options.get('make-options', None)
        if self.make_options:
            make_options = ' '.join(self.make_options.split())
        else:
            make_options = ''
        make = self.options.get('make-binary', 'make')
        logger.debug("%s %s" % (make, make_options))
        system("%s %s" % (make, make_options))
        system("%s %s install" % (make, make_options))
