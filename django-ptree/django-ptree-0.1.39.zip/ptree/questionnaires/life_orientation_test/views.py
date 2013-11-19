import ptree.views.abstract
import ptree.questionnaires.life_orientation_test.forms as forms

class ViewInThisApp(object):
    url_base = 'LOT_R'

class LifeOrientationTest(ptree.views.abstract.CreateView, ViewInThisApp):
    form_class = forms.LifeOrientationTestForm
    template_name = 'life_orientation_test/Questionnaire.html'