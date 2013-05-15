#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, fields, ModelSQL
from trytond.wizard import Wizard, StateTransition, StateView, StateTransition, Button
from trytond.transaction import Transaction
from trytond.pool import Pool
import json
from lxml import etree
 
try:
    import hashlib
except ImportError:
    hashlib = None
    import md5
    
class MassEditingWizInit(ModelView, ModelSQL):
    _name = 'mass.editing.init'
    _description = __doc__
    company_image = fields.Binary('Image') 
    active_model = fields.Char('Active')
    active_ids = fields.Char('Active Ids')
    
    
    def default_active_model(self):
        '''
        Return default value of Active Model
        '''
        return Transaction().context.get('active_model')
    
    def default_active_ids(self):
        '''
        Return list of current Ids
        '''
        if Transaction().context.get('active_ids'):
            return str(Transaction().context.get('active_ids'))
        
    def __init__(self):
        super(MassEditingWizInit, self).__init__()
        self._buttons.update({
                'cancel': {
                },
                'action_apply': {
                }
        })
    
    def fields_view_get(self, view_id=None, view_type='form', hexmd5=None):
    
    # It filter the fields that we select on a model
    
        res = super(MassEditingWizInit, self).fields_view_get(view_id, view_type, hexmd5)
        pool = Pool()
        ir_model_object = pool.get('ir.model') # It return  ir_model_object like <trytond.ir.model.Model object at 0x7f7ab10176d0>
        ir_model_ids = ir_model_object.search([('model', '=', Transaction().context.get('active_model'))]) # It store ir_model ids like ir_model_ids [73]
        ir_model_data = ir_model_object.browse(ir_model_ids)[0].name  # It store model data like ir_model_data Mass Editing
        mass_object = pool.get('mass.editing')
        mass_ids = mass_object.search([('model_id', '=', ir_model_data)])
        for mass_data in self.browse(mass_ids):
            data = mass_data.id
        if data:
            editing_data = mass_object.browse(data)
            fields = {}
            xml_form = etree.Element('form', {'string': editing_data.name})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            etree.SubElement(xml_group, 'field', {'name': 'company_image', 'nolabel': '1','colspan': '1', 'widget':'image'})
            etree.SubElement(xml_group, 'label', {'string': '','colspan': '2'})
            fields['company_image'] = {'type':'binary', 'string':''}
            etree.SubElement(xml_group, 'field', {'name': 'active_model','colspan': '1','invisible' : '1'})
            etree.SubElement(xml_group, 'label', {'string': '','colspan': '2'})
            fields['active_model'] = {'type':'char', 'string':''}
            etree.SubElement(xml_group, 'field', {'name': 'active_ids','colspan': '1','invisible' : '1'})
            etree.SubElement(xml_group, 'label', {'string': '','colspan': '2'})
            fields['active_ids'] = {'type':'char', 'string':''}
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            model_object = pool.get(Transaction().context.get('active_model'))
            for field in editing_data.model_field_ids:
                if field.ttype == 'many2many':
                    model_field = model_object.fields_get([field.name])
                    fields[field.name] = model_field[field.name]
                    fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove_m2m','Remove'),('add','Add')]}
                    xml_group = etree.SubElement(xml_group, 'group', {'colspan': '4'})
                    etree.SubElement(xml_group, 'separator', {'string': model_field[field.name]['string'],'colspan': '2'})
                    etree.SubElement(xml_group, 'newline'),
                    etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name,'nolabel':'1','colspan' : '2'})
                    etree.SubElement(xml_group, 'field', {'name': field.name, 'nolabel' : '1','colspan' : '4'})
                elif field.ttype == 'many2one':
                    model_field = model_object.fields_get([field.name])
                    if model_field:
                        fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                        fields[field.name] = {'type':field.ttype, 'string': field.field_description, 'relation': field.relation}
                        etree.SubElement(xml_group, 'separator', {'string': model_field[field.name]['string'],'colspan': '2'})
                        etree.SubElement(xml_group, 'newline')
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan':'2'})
                        etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1','colspan':'2'})
                elif field.ttype == "char":
                    model_field = model_object.fields_get([field.name])
                    fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    fields[field.name] = {'type':field.ttype, 'string': field.field_description}
                    etree.SubElement(xml_group, 'newline')
                    etree.SubElement(xml_group, 'separator', {'string': model_field[field.name]['string'],'colspan': '2'})
                    etree.SubElement(xml_group, 'newline')
                    etree.SubElement(xml_group, 'field', {'name': "selection_" + field.name,'colspan':'2', 'colspan':'2'})
                    etree.SubElement(xml_group, 'field', {'name': field.name, 'nolabel':'1', 'colspan':'2'})
                elif field.ttype == 'selection':
                    model_field = model_object.fields_get([field.name])
                    fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    model_field = model_object.fields_get([field.name])
                    etree.SubElement(xml_group, 'separator', {'string': model_field[field.name]['string'],'colspan': '2'})
                    etree.SubElement(xml_group, 'newline')
                    etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan':'2'})
                    etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1','colspan':'2'})
                    fields[field.name] = {'type':field.ttype, 'string': field.field_description, 'selection': model_field[field.name]['selection']}
                else:
                    model_field = model_object.fields_get([field.name])
                    fields[field.name] = {'type':field.ttype, 'string': field.field_description}
                    fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(xml_group, 'group', {'colspan': '6'})
                        etree.SubElement(xml_group, 'separator', {'string': fields[field.name]['string'],'colspan': '2'})
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name,'colspan': '2','nolabel':'1'})
                        etree.SubElement(xml_group, 'field', {'name': field.name, 'colspan':'4', 'nolabel':'1'})
                    else:
                        fields["selection_"+field.name] = {'type':'selection', 'string': model_field[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan': '2',})
                        etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1','colspan': '2',})
            etree.SubElement(xml_form, 'separator', {'string' : '','colspan': '6'})
            xml_group3 = etree.SubElement(xml_form, 'group', {'col': '2', 'colspan': '2'})
            etree.SubElement(xml_group3, 'button', {'string' :'Apply', 'type' :'object','name':"action_apply"})

            root = xml_form.getroottree()
            res['arch'] = etree.tostring(root)
            res['fields'] = fields
        return res
    
    def create(self, vals):
        '''
        Set/Remove the values of fields in selected records.
        
        :param vals: statndard dictionay
        '''
        active_ids = json.loads(vals.get('active_ids'))
        if vals.get('active_model') and active_ids:
            model_object = Pool().get(vals.get('active_model'))
            res = {}
            for k,v in vals.items():
                if k.startswith('selection_'):
                    split_key= k.split('_',1)[1]
                    if v == 'set':
                        res.update({split_key: vals.get(split_key, False)})
                    elif v == 'remove':
                        res.update({split_key: ''})
                    elif v == 'remove_m2m':
                        res.update({split_key: [("unlink_all",0,[])]})
                    elif v == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][1]:
                            m2m_list.append(("add", m2m_id))
                            res.update({split_key: m2m_list})
            if res:
                model_object.write(active_ids, res)
        result = super(MassEditingWizInit, self).create({})
        return result
        
    def action_apply(self, ids):
        return  {'type': 'ir.action.act_window_close'}
    
MassEditingWizInit()

class MassEditingWizCreate(Wizard):
    _name = 'mass.editing.create'
    start = StateView('mass.editing.init',
                      'new_mass_editing.view_mass_editing_wiz', [
                    Button('Cancel', 'end', 'tryton-cancel'),
                    ])
    
MassEditingWizCreate() 