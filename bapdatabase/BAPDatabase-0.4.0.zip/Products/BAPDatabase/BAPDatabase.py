import os
from os.path import join, dirname, splitext

try:
    import json
except ImportError:
    import simplejson as json

from z3c.sqlalchemy.util import registeredWrappers, createSAWrapper
from sqlalchemy.orm.exc import NoResultFound
from ZPublisher import NotFound
from zope.interface import implements

from App.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

from Products.BAPDatabase.interfaces import IBAPDatabase

import models

tables = {}
for f in os.listdir(join(dirname(__file__), 'zpt')):
    if f.endswith('.zpt'):
        fname = splitext(f)[0]
        tables.setdefault(fname,
                            PageTemplateFile('zpt/%s' % fname, globals()))

def create_object_callback(parent, id):
    ob = BAPDatabase(id)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    return ob

manage_add_html = PageTemplateFile('zpt/manage_add', globals())
def manage_add_bap(self, id, REQUEST=None, **kwargs):
    """ Create new BAPDatabase object from ZMI.
    """
    create_object_callback(self, id)
    ob = self._getOb(id)
    if REQUEST is not None:
        params = dict(REQUEST.form)
    else:
        params = kwargs
    ob.db_host = params.pop('db_host', None)
    ob.db_port = params.pop('db_port', None)
    ob.db_username = params.pop('db_username', None)
    ob.db_password = params.pop('db_password', None)
    ob.db_name = params.pop('db_name', None)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob


class BAPDatabase(BTreeFolder2):
    """
        BAPDatabase object, folder-type that contains items described within specs.
        This is the root of the application.
    """
    implements(IBAPDatabase)
    meta_type = 'BAPDatabase'
    security = ClassSecurityInfo()

    db_host = None
    db_port = None
    db_username = None
    db_password = None
    db_name = None
    db_debug = False

    # def _get_schema(self):
    #     from Products.NaayaCore.constants import ID_SCHEMATOOL
    #     return self.getSite()._getOb(ID_SCHEMATOOL).getSchemaForMetatype('Naaya Folder')

    def __init__(self, id):
        """
            Constructor that builds new BAPDatabase object.
        """
        super(BAPDatabase, self).__init__(id)

    def _get_session(self):
        """ Create a Z3C.SQLAlchemy registered wrapper """
        if self.db_name in registeredWrappers.keys():
            wrapper = registeredWrappers[self.db_name]
        else:
            wrapper = createSAWrapper('mysql://%s:%s@%s:%d/%s?charset=utf8&use_unicode=0' \
                                      % (self.db_username, self.db_password, self.db_host, int(self.db_port), self.db_name),
                                      name=self.db_name,
                                      engine_options = {'echo' : self.db_debug})
        return wrapper.session

    def _delete_wrapper(self):
        """
            Delete the Z3C.SQLAlchemy registered wrapper
        """
        if self.db_name in registeredWrappers.keys():
            del registeredWrappers[self.db_name]
            self._p_changed = 1

    def get_countries(self):
        countries = self._get_session().query(models.Header.Country) \
                                        .order_by(models.Header.Country).all()
        return [ country[0] for country in countries if country ]

    def get_country_code(self, country):
        return self._get_session().query(models.Header.CountryCode) \
                                .filter(models.Header.Country == country).one()[0]

    def get_objectives(self):
        return self._get_session().query(models.Objective) \
                                .order_by(models.Objective.order).all()

    def get_objective(self, objective_id):
        try:
            return self._get_session().query(models.Objective) \
                                    .filter(models.Objective.id == objective_id).one()
        except NoResultFound:
            raise NotFound, "Objective not found"

    def get_objective_by_name(self, objective_name):
        """ """
        try:
            return self._get_session().query(models.Objective) \
                                    .filter(models.Objective.name == objective_name).one()
        except NoResultFound:
            return

    def get_targets(self, objective_id, country):
        return self._get_session().query(models.Target) \
                    .join((models.CountryReport, models.CountryReport.Ident == models.Target.id)) \
                    .filter(models.CountryReport.Country == country) \
                    .filter(models.Target.objective == objective_id) \
                    .order_by(models.Target.id).all()

    def get_target(self, target_id):
        try:
            return self._get_session().query(models.Target).filter(models.Target.id == target_id).one()
        except NoResultFound:
            raise NotFound, "Target not found"

    def get_target_parents(self, target):
        return self.get_objective(target.objective)

    def get_objective_targets(self, objective_id):
        return self._get_session().query(models.Target) \
                                .filter(models.Target.objective == objective_id) \
                                .order_by(models.Target.id).all()

    def get_country_actions(self, objective_id, target_id, country):
        return self._get_session().query(models.Action) \
                    .join((models.CountryReport, models.CountryReport.Ident == models.Action.id)) \
                    .filter(models.CountryReport.Country == country) \
                    .filter(models.CountryReport.Objective == objective_id) \
                    .filter(models.Action.target == target_id).all()

    def get_action(self, action_id):
        try:
            return self._get_session().query(models.Action).filter(models.Action.id == action_id).one()
        except NoResultFound:
            raise NotFound, "Action not found"

    def get_actions(self, target_id=None, objective_id=None):
        records = self._get_session().query(models.Action) \
                        .join((models.Target, models.Target.id == models.Action.target))

        if target_id:
            records = records.filter(models.Action.target == target_id)

        if objective_id:
            records = records.filter(models.Target.objective == objective_id)

        return records.all()

    def get_action_parents(self, action_id):
        record = self._get_session().query(models.Target) \
                    .join((models.Action, models.Target.id == models.Action.target)) \
                    .filter(models.Action.id == action_id).one()
        target = self.get_target(record.id)
        objective = self.get_objective(record.objective)
        return target, objective

    def get_report(self, table_id, country):
        try:
            code = self.get_country_code(country)
            model = getattr(models, table_id)
            return self._get_session().query(model).filter(model.CountryCode == code).one()
        except NoResultFound:
            pass
        return None

    def get_community_report(self, action_id):
        return self._get_session().query(models.CommunityReport) \
                                .filter(models.CommunityReport.action == action_id) \
                                .order_by(models.CommunityReport.year).all()

    def get_country_report(self, id, country, mop=''):
        try:
            return self._get_session().query(models.CountryReport) \
                                .filter(models.CountryReport.Ident == id) \
                                .filter(models.CountryReport.MOP == mop) \
                                .filter(models.CountryReport.Country == country).one()
        except NoResultFound:
            return

    def get_progress_measure(self, action_id, mop=''):
        try:
            return self._get_session().query(models.ProgressMeasures) \
                                    .filter(models.ProgressMeasures.id == action_id) \
                                    .filter(models.ProgressMeasures.mop == mop).one()
        except NoResultFound:
            return

    def get_table(self, action_id, country):
        try:
            if country == 'Community report':
                text = "\n\n".join([mop.progress for mop in self.get_community_report(action_id) if mop.progress])
                return self.compare_community_details.__of__(self)(text=text)
            else:
                template = tables.get(action_id)
                if template is not None:
                    return template.__of__(self)(country=country, action_id=action_id)
        except:
            pass
        return self.empty_table.__of__(self)()

    def json_get_targets(self, objective_name):
        """ """
        objective = self.get_objective_by_name(objective_name)
        records = []

        for target in self.get_objective_targets(objective.id):
            description = 'Target %s: %s' % (target.name, target.description)
            records.append({
                'optionValue': target.id,
                'optionDisplay': target.name,
                'optionTitle': description,
            })

        return json.dumps(records)

    def json_get_comparision_countries(self, ref_country):
        """ """
        records = []
        for country in self.get_countries():
            if country != ref_country:
                records.append({'optionValue': country,
                                'optionDisplay': country,
                                'optionTitle': country})
        return json.dumps(records)

    index_html = PageTemplateFile('zpt/index', globals())

    objective = PageTemplateFile('zpt/objective_details', globals())
    target = PageTemplateFile('zpt/target_details', globals())
    action = PageTemplateFile('zpt/action_details', globals())

    compare = PageTemplateFile('zpt/compare', globals())
    compare_details = PageTemplateFile('zpt/compare_details', globals())

    compare_multiple = PageTemplateFile('zpt/compare_multiple', globals())
    compare_side_by_side = PageTemplateFile('zpt/compare_side_by_side', globals())
    compare_community_details = PageTemplateFile('zpt/compare_community_details', globals())

    empty_table = PageTemplateFile('zpt/empty_table', globals())

    community_report = PageTemplateFile('zpt/community_report', globals())
    community_objective = PageTemplateFile('zpt/community_objective', globals())
    community_target = PageTemplateFile('zpt/community_target', globals())
    community_action = PageTemplateFile('zpt/community_action', globals())

InitializeClass(BAPDatabase)