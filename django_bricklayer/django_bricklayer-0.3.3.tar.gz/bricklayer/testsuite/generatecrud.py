from django.conf import settings
from django.test import TestCase
from django.utils.module_loading import import_module
from bricklayer.utils import run_manage_py, exists_path, exists_dir
import django, inspect, os, compileall, imp


        
class GenerateCRUDTestCase(TestCase):
    def setUp(self):
        run_manage_py("generatecrud test_app -m TestModel")
        import test_app
        self.app_path = os.path.abspath(test_app.__path__[0])
        compileall.compile_dir(self.app_path, force=1)
    
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
        
    def tearDown(self):
        app_path = self.app_path
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_form.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_list.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_detail.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_confirm_delete.html'))
        os.rmdir(os.path.join(app_path, 'templates','test_app'))
        os.rmdir(os.path.join(app_path, 'templates'))
        os.remove(os.path.join(app_path, 'urls.py'))
        try:
            os.remove(os.path.join(app_path, 'forms.py'))
        except: pass
        
        os.remove(os.path.join(app_path, 'views.py'))
        with open(os.path.join(app_path, 'views.py'),"w") as f:
                f.write("")
        
        root_urlconf_path = inspect.getsourcefile(import_module(settings.ROOT_URLCONF)) 
        with open(root_urlconf_path, "w+") as f:
            urls_text = f.read()
            extend_patterns = 'urlpatterns+=patterns("",url(r"testmodel/",include("test_app.urls")),)'
            urls_text = urls_text.replace(extend_patterns, "\n")
            f.write(urls_text)
            
class GenerateCRUDandFormTestCase(TestCase):
    def setUp(self):
        import test_app
        self.app_path = os.path.abspath(test_app.__path__[0])
        with open(os.path.join(self.app_path, 'views.py'),'w+') as f:
            views = f.read()
            views = views.strip()
            if views != '':
                f.write("")
        run_manage_py("generatecrud test_app -m TestModel -f")
        compileall.compile_dir(self.app_path, force=1)
        
        
     
    def test_form_py(self):
        self.assertTrue(exists_path(self.app_path, 'forms.py'))
        forms_module = dir(imp.load_source("forms", os.path.join(self.app_path, "forms.py")))
        self.assertIn("forms", forms_module)
        self.assertIn("TestModelForm", forms_module)
     
    def test_view_py(self):
        app_path = self.app_path
        forms = imp.load_source("forms",os.path.join(app_path, 'forms.py')) 
        views = imp.load_source("views",os.path.join(app_path, 'views.py'))
        self.assertTrue(hasattr(views, "TestModelCreate"))
        self.assertTrue(hasattr(views, "TestModelUpdate"))
        self.assertTrue(hasattr(forms, "TestModelForm"))
     
    def tearDown(self):
        app_path = self.app_path
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_form.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_list.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_detail.html'))
        os.remove(os.path.join(app_path,'templates','test_app','testmodel_confirm_delete.html'))
        os.rmdir(os.path.join(app_path, 'templates','test_app'))
        os.rmdir(os.path.join(app_path, 'templates'))
        os.remove(os.path.join(app_path, 'urls.py'))
        try:
            os.remove(os.path.join(app_path, 'forms.py'))
        except: pass
        
        os.remove(os.path.join(app_path, 'views.py'))
        with open(os.path.join(app_path, 'views.py'),"w") as f:
                f.write("")
        
        root_urlconf_path = inspect.getsourcefile(import_module(settings.ROOT_URLCONF)) 
        with open(root_urlconf_path, "w+") as f:
            urls_text = f.read()
            extend_patterns = 'urlpatterns+=patterns("",url(r"testmodel/",include("test_app.urls")),)'
            urls_text = urls_text.replace(extend_patterns, "\n")
            f.write(urls_text)