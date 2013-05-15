#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateAction, StateView, StateTransition, Button

class mass_editing(ModelSQL, ModelView):
    'Mass Editing'
    _name = 'mass.editing'
    _description = __doc__

#   Here we Define a different fields use in mass editind module

    name = fields.Char('Name', size=64, required=True)
    model_id = fields.Many2One('ir.model', 'Model', on_change=['model_id'], required=True)
    model_field_ids = fields.Many2Many('mass.editing-ir.model.field', 'mass_id', 'field_id', 'Fields')
    
#   The ref_ir_action_wizard store a side bar action like show view,add shortcut,open shortcut,graph etc.
    ref_ir_action_wizard = fields.Many2One('ir.action.wizard', 'Sidebar Action')
    
#   The ref_ir_value store the sidebar button of it.translation model 
    ref_ir_value = fields.Many2One('ir.translation', 'Sidebar Button')
    model_list = fields.Char('Model List', size=64)
 
#   the cunstruction will be call when it first upload of molel and update two button create and remove    
    def __init__(self):
        super(mass_editing, self).__init__()
        self._rpc.update({'create_mass_editing_aa': True})
        self._buttons.update({
                'create_mass_editing': {
                    },
                'remove_mass_editing': {
                    }
                })
        
    def on_change_model_id(self, vals):
        res = {} # create a blank space dictionary
        pool = Pool()
        if vals['model_id']:
            model_obj = pool.get('ir.model')  # model_obj store <trytond.ir.model.Model object at 0x7fd04d025f90> that we selected model 
            model_data = model_obj.browse(vals['model_id']) # it store BrowseRecord(ir.model, 73) of model
            model_list = "[" + str(vals['model_id']) + ""
            new_model_obj = pool.get(model_data.model) # it store new_model_obj <trytond.modules.new_mass_editing.mass_editing.mass_editing object 
            										   # at 0x7fd04cf45610> that we select of model 																																					
            if new_model_obj._inherits:
                    for key, val in new_model_obj._inherits.items():
                        model_ids = model_obj.search([('model_id', '=', key)])
                        if model_ids:
                            model_list += "," + str(model_ids[0]) + ""
            model_list += "]"
            
            # model list store the id of model_list [73] that it store
            res['model_list'] = model_list
        return res
    
    @ModelView.button
    def create_mass_editing(self, ids):
        ''' 
        Create Action for the Module which select in Model
        
        :param ids: List of ids
        return True
        '''
        
        pool = Pool()
        vals = {}
        res = {}
        key = {}
        action_obj = pool.get('ir.action.act_window')
        wiz_object = pool.get('ir.action.wizard')
        keyword_object = pool.get('ir.action.keyword')
        model_data_obj = pool.get('ir.model.data')
        for model_data in self.browse(ids):
            obj = model_data.model_id.model
            button_name = ('Mass Editing (%s)') % model_data.name
            res = {
                'name' : button_name,
                'wiz_name' : 'mass.editing.create',
                'model' : obj,
            }
            new_wiz_id = wiz_object.create(res)
            vals['ref_ir_action_wizard'] = new_wiz_id
            key = {
                'keyword' : 'form_action',
                'model' : str(obj) + ',' +str(-1),
                'action': new_wiz_id
            }
            key_id = keyword_object.create(key)
        self.write(ids, vals)
        return True
    
    @ModelView.button
    def remove_mass_editing(self, ids):
        '''
        Remove the Action
        
        :param ids: List of ids
        return True
        '''
        pool = Pool()
        for data in self.browse(ids):
            if data.ref_ir_action_wizard:
                pool.get('ir.action.wizard').delete(data.ref_ir_action_wizard.id)
        return True
    
mass_editing()

class mass_fields(ModelSQL):
    _name = 'mass.editing-ir.model.field'
    _table = 'mass_relation_field'
    mass_id = fields.Many2One('mass.editing', 'Mass', required=True)
    field_id = fields.Many2One('ir.model.field', 'Field', required=True)

mass_fields()