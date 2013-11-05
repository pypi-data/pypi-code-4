from django.conf import settings
from django.test import TestCase
from django.utils.module_loading import import_module
from bricklayer.utils import run_manage_py, exists_path, exists_dir
import django, inspect, os, compileall, imp

class BricklayerTestCase(TestCase):
    def setUp(self):
        import test_app
        self.app_path = os.path.abspath(test_app.__path__[0])
        compileall.compile_dir(self.app_path, force=1)

    def tearDown(self):
        app_path = self.app_path
        try:
            os.remove(os.path.join(app_path,'templates','test_app','testmodel_form.html'))
        except: pass
        try:
            os.remove(os.path.join(app_path,'templates','test_app','testmodel_list.html'))
        except: pass
        try:    
            os.remove(os.path.join(app_path,'templates','test_app','testmodel_detail.html'))
        except: pass
        try:
            os.remove(os.path.join(app_path,'templates','test_app','testmodel_confirm_delete.html'))
        except: pass 
        try:
            os.rmdir(os.path.join(app_path, 'templates','test_app'))
        except: pass    
        try:
            os.rmdir(os.path.join(app_path, 'templates'))
        except: pass
        try:
            os.remove(os.path.join(app_path, 'urls.py'))
        except: pass
        try:
            os.remove(os.path.join(app_path, 'forms.py'))
        except: pass
        try:
            with open(os.path.join(app_path, 'views.py'),"w") as f:
                f.write("")
        except: pass        

        # Remove urlpatterns from ROOT_URLCONF
        try:
            root_urlconf_path = inspect.getsourcefile(import_module(settings.ROOT_URLCONF)) 
            with open(root_urlconf_path, "r") as f:
                urls_text = "".join(f.readlines())
            with open(root_urlconf_path, "w") as f:
                extend_patterns = 'urlpatterns+=patterns("",url(r"testmodel/",include("test_app.urls")),)'
                urls_text.replace(extend_patterns, "\n")
                f.write(urls_text)
        except: pass

class GenerateCRUDTestCase(BricklayerTestCase):
    def setUp(self):
        run_manage_py("generatecrud test_app -m TestModel")
        super(GenerateCRUDTestCase, self).setUp()
    
    def test_views(self):
        from test_app import views as views_py
        
        msg = "views.py contains " + ",".join(dir(views_py))
        with open(os.path.join(self.app_path, "views.py")) as f:
            msg += "".join(f.readlines())
        self.assertTrue(hasattr(views_py, "TestModelCreate"), msg)
    
        
    def test_crud_files(self):
        app_path = self.app_path
        self.assertTrue(exists_path(app_path,'urls.py'))
        self.assertTrue(exists_path(app_path,'templates'))
        self.assertTrue(exists_dir( app_path,'templates'))
        self.assertTrue(exists_dir( app_path,'templates', 'test_app'))
        self.assertTrue(exists_path(app_path,'templates','test_app','testmodel_form.html'))
        self.assertTrue(exists_path(app_path,'templates','test_app','testmodel_list.html'))
        self.assertTrue(exists_path(app_path,'templates','test_app','testmodel_detail.html'))
        self.assertTrue(exists_path(app_path,'templates','test_app','testmodel_confirm_delete.html'))
        
            
class GenerateCRUDandFormTestCase(BricklayerTestCase):
    def setUp(self):
        run_manage_py("generatecrud test_app -m TestModel -f")
        super(GenerateCRUDandFormTestCase, self).setUp()
    
    
    def test_form_py(self):
        from test_app import forms as forms_py
        import test_app as app
        self.assertTrue(exists_path(self.app_path, 'forms.py'))
        self.assertTrue(hasattr(forms_py,"forms"))
        self.assertTrue(getattr(forms_py, "forms",None) is django.forms )
        self.assertTrue(getattr(forms_py,"TestModel") is app.models.TestModel)
    
    def test_view_py(self):
        app_path = self.app_path
        forms = imp.load_source("forms",os.path.join(app_path, 'forms.py')) 
        views = imp.load_source("views",os.path.join(app_path, 'views.py'))
        self.assertTrue(hasattr(views, "TestModelCreate"))
        self.assertTrue(hasattr(views, "TestModelUpdate"))
        self.assertTrue(hasattr(forms, "TestModelForm"))
    

        
    