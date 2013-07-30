from potools import pounique
import os
import tempfile
import unittest
import shutil
import optparse

class TestPoUniqueFiles(unittest.TestCase):
    """ """

    def _get_optargs(self, **kw):
        args = [os.getcwd()+'/../../potools/tests/locales/test.po',
                os.getcwd()+'/../../potools/tests/locales2/test.po']
        opts = {'best': False, 'sort': False, 'output': None}
        opts.update(kw)
        return pounique.parse_options(args, optparse.Values(opts))

    def test_unique_last(self):
        options, args = self._get_optargs()
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        mapping = {}
        for entry in entries:
            mapping[entry.msgid] = entry.msgstr
            
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'', 
                           u'label_foo': u'Foobar', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo',
                           u'Keep it empty': u'',
                           })

    def test_unique_best(self):
        options, args = self._get_optargs(best=True)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        mapping = {}
        for entry in entries:
            mapping[entry.msgid] = entry.msgstr
            
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo',
                           u'Keep it empty': u'',
                           })

    def test_unique_sorted(self):
        options, args = self._get_optargs(sort=True)
        unique = pounique.PoUnique(args=args, options=options)
        
        entries = list(unique._get_unique(args))
        
        self.assertEquals(
            [x.msgid for x in entries], 
            [u'Baz', u'bazoo', u'Hello World', u'Keep it empty', u'label_bar', u'label_foo'])


class TestPoUniqueFolders(unittest.TestCase):
    """ """

    def _get_optargs(self, **kw):
        args = [os.path.normpath(os.getcwd()+'/../../potools/tests/locales/'),
                os.path.normpath(os.getcwd()+'/../../potools/tests/locales2/')]
        
        opts = {'best': False, 'sort': False, 'output': None}
        opts.update(kw)
        return pounique.parse_options(args, optparse.Values(opts))

    def test_dir(self):
        try:
            outdir = tempfile.mkdtemp()
            options, args = self._get_optargs(output=outdir)
            
            unique = pounique.PoUnique(args=args, options=options)
            
            self.assertEquals(unique._get_all_unique_paths(),
                              set(['test.po']))

            self.assertEquals(list(unique._get_all_comparisons()),
                              [('test.po', [args[0] + '/test.po', args[1] + '/test.po'])])
            
        finally:
            shutil.rmtree(outdir)