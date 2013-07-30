from potools import poupdate, popopulate
import os
import polib
import tempfile
import unittest
import shutil
import optparse

class TestPoUpdateFiles(unittest.TestCase):
    """ """

    def setUp(self):
        self.target = tempfile.mkstemp()[1]
        shutil.copy(os.getcwd()+'/../../potools/tests/locales/test.po',
                    self.target)
        self.source = os.getcwd()+'/../../potools/tests/locales2/test.po'
        
    def tearDown(self):
        os.unlink(self.target)
        
    def _get_optargs(self, **kw):        
        opts = {'insert_new': False, 'force': False, 'use_fuzzy': False}
        opts.update(kw)
        return poupdate.parse_options([self.target, self.source], optparse.Values(opts))

    def test_update(self):
        options, args = self._get_optargs()
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World',
                           })
        
    def test_update_insert_new(self):
        """Add back new messages that doesn't exist in source, even if they are empty"""
        options, args = self._get_optargs(insert_new=True)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foo', 
                           u'Hello World': u'Hello World',
                           u'bazoo': u'Bazoo',
                           u'Keep it empty': u'',
                           })
        
    def test_update_force(self):
        """Overwrite all target messages, no matter if the source is empty or fuzzy"""
        options, args = self._get_optargs(force=True)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        
        update = polib.pofile(self.target)
        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'', 
                           u'label_foo': u'Foobar', 
                           u'Hello World': u'Hello World',
                           })
        

class TestPoUpdateFilesFuzzy(unittest.TestCase):
    """Tests that empty is not replaced by fuzzy when using -s"""

    def setUp(self):
        # First make an popopulated source copt of locales2/test.po
        self.source = tempfile.mkstemp()[1]
        self.target = tempfile.mkstemp()[1]
        options, args = popopulate.parse_options(
            [os.getcwd()+'/../../potools/tests/locales2/test.po', self.source],
            optparse.Values({'verbose': False, 'update': False})
        )

        popopulate.PoPopulate(args=args, options=options).run()
        shutil.copy(os.getcwd()+'/../../potools/tests/locales2/test.po', self.target)
                
    def tearDown(self):
        os.unlink(self.source)
        os.unlink(self.target)
        
    def _get_optargs(self, **kw):        
        opts = {'insert_new': False, 'force': False, 'use_fuzzy': False}
        opts.update(kw)
        return poupdate.parse_options([self.target, self.source], optparse.Values(opts))

    def test_update_not_insert_fuzzy(self):
        """Add back messages for empty targets, even if the source message is fuzzy."""
        options, args = self._get_optargs(use_fuzzy=False)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        update = polib.pofile(self.target)

        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'', 
                           u'label_foo': u'Foobar', 
                           u'Keep it empty': u'',
                           u'bazoo': u'Bazoo',
                           })

    def test_update_insert_fuzzy(self):
        """Add back messages for empty targets, even if the source message is fuzzy."""
        options, args = self._get_optargs(use_fuzzy=True)
        update = poupdate.PoUpdate(args=args, options=options)
        
        update.run()
        update = polib.pofile(self.target)

        mapping = {}
        for entry in update:
            mapping[entry.msgid] = entry.msgstr
                    
        self.assertEquals(mapping, 
                          {u'Baz': u'Bazzza!', 
                           u'label_bar': u'Bar', 
                           u'label_foo': u'Foobar', 
                           u'Keep it empty': u'Keep it empty',
                           u'bazoo': u'Bazoo',
                           })
                