# -*- coding: utf-8 -*-

"""Recipe for applying patches"""

import logging
logger = logging.getLogger('patch')

from hashlib import sha1
import os
from subprocess import Popen, PIPE, STDOUT

import zc.buildout
import zc.recipe.egg


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.patcher = self.egg_or_path(self.options)
        self.patches = self.get_patches(self.options)
        if 'patch' in self.options:
            del self.options['patch']
        if 'patches' in self.options:
            del self.options['patches']
        self.options['hashes'] = str(list(self.calculate_hashes(self.patches)))
        self.options['python'] = self.buildout['buildout']['python']
        self.options['executable'] = self.buildout[self.options['python']]['executable']
        self.options['eggs-directory'] = buildout['buildout']['eggs-directory']
        self.options['develop-eggs-directory'] = buildout['buildout']['develop-eggs-directory']

    def install(self):
        """Installer"""
        for patch in self.patches:
            self.patcher(patch)
        return ()

    def update(self):
        """Updater"""
        return ()

    @staticmethod
    def get_patches(options):
        """Returns a list of patches."""
        patches = options.get('patches')
        patch = options.get('patch')
        if patch is not None and patches is None:
            patches = patch
        elif patch is not None and patches is not None:
            raise zc.buildout.UserError('Provide only the patches option.')
        return [os.path.realpath(p) for p in patches.strip().split('\n')]

    @staticmethod
    def calculate_hashes(patches):
        """Yields (pathname, SHA1 digest) for each file in `patches`."""
        for patch in patches:
            try:
                yield (patch, sha1(open(patch).read()).hexdigest())
            except IOError:
                raise zc.buildout.UserError('Patch cannot be read: %s' % patch)

    def egg_or_path(self, options):
        """Decides whether to apply patches to eggs or paths."""
        egg = options.get('egg')
        path = options.get('path')
        if egg is not None and path is not None:
            raise zc.buildout.UserError('Provide either an egg or path option.')
        elif egg is not None:
            return self.patch_egg
        else:
            return self.patch_path

    def install_egg(self, egg):
        """Installs the specified `egg`."""
        links = self.buildout['buildout'].get('find-links', [])
        if links:
            links = tuple(links.split('\n'))
        ws = zc.buildout.easy_install.install(
            [egg], self.options['develop-eggs-directory'],
            links           = links,
            index           = self.buildout['buildout'].get('index'),
            executable      = self.options['executable'],
            path            = [self.options['eggs-directory']],
            newest          = self.buildout['buildout'].get('newest') == 'true',
            allow_hosts     = self.buildout['buildout'].get('allow-hosts', '*'),
            always_unzip    = 'true', )
        return ws.require(egg)[0].location

    def patch_egg(self, patch):
        """Installs an egg and patches it with `patch`."""
        if getattr(self, 'egg_path', None) is None:
            self.egg_path = self.install_egg(self.options['egg'])
        return self.use_patch_binary(self.egg_path, patch)

    def patch_path(self, patch):
        """Patches a path with `patch`."""
        return self.use_patch_binary(self.options['path'], patch)

    def use_patch_binary(self, path, patch):
        """Applies a `patch` to `path` using an external binary."""
        logger.info('reading patch %s' % patch)
        logger.info('in %s...' % path)

        # Call
        command = ['patch', '-p0', '-N']
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=path)
        output = p.communicate(open(patch).read())[0]

        # Log
        output = output.strip()
        for line in output.strip().split('\n'):
            logger.info(line)

        # Ok
        if p.returncode == 0:
            return path

        # XXX "patch -N" is broken actually...
        # See http://unix.stackexchange.com/questions/65698/how-to-make-patch-ignore-already-applied-hunks
        already = 'Reversed (or previously applied) patch detected!' in output
        if p.returncode == 1 and already is True:
            logger.warn("Patch already applied, or something worse?")
            return path

        # Error
        raise zc.buildout.UserError('could not apply %s' % patch)
