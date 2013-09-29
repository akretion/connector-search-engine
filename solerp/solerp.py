from openerp.osv import fields, osv, orm
from openerp.osv.orm import Model, TransientModel, AbstractModel
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import sunburnt
from unidecode import unidecode


class solr_config_settings(TransientModel):

    _name = 'solr.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'solr_url' : fields.char('SolR URL', size=128),
        'solr_language_id': fields.many2one('res.lang', 'Language')
    }

    def get_default_solr_language_id(self, cr, uid, field_names, context=None):
        solr_language_id = self.pool.get("ir.config_parameter").get_param(cr, uid, "solr.language_id", context=context)
        return {'solr_language_id': solr_language_id}

    def get_default_solr_url(self, cr, uid, field_names, context=None):
        solr_url = self.pool.get("ir.config_parameter").get_param(cr, uid, "solr.url", context=context)
        return {'solr_url': solr_url}

    def set_alias_domain(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "solr.url", record.solr_url or '', context=context)
            config_parameters.set_param(cr, uid, "solr.language_id", record.solr_language_id and record.solr_language_id.id, context=context)
        return True

    def get_solr_interface(self, cr, uid, context=None): #TODO hook to specify collection
        solr_url = self.pool.get("ir.config_parameter").get_param(cr, uid, "solr.url", context=context)
        if solr_url:
            return sunburnt.SolrInterface(solr_url.encode('utf-8'))
        else:
            return None

    def index_all(self, cr, uid, ids, context=None):
        for model_name, model_obj in self.pool.models.iteritems():
            if hasattr(model_obj, '_solr_collection_mixin') and model_name != 'solr.collection.mixin':
                res_ids = model_obj.search(cr, uid, [], context=context)
                model_obj.write(cr, uid, res_ids, {'active': True}, context)


class solr_mixin(AbstractModel):
    _description='SolR mixin'
    _name = 'solr.mixin'
    _solr_index_alone = True

    def _get_included_relations(self, cr, uid, context=None):
        return []

    def _get_skipped_fields(self, cr, uid, context=None):
        return []

    def _solr_key(self, field_type):
        return {
            'char': "%s_s",
            'text': "%s_s",
            'integer': "%s_i",
            'float': "%s_f",
            'boolean': "%s_b",
            'many2one': "%s_s",
            'one2many': "%s_sm",
            'many2many': "%s_sm",
        }.get(field_type, "%s_s")

    def _field_to_solr(self, cr, uid, field, field_type, relation, included_relations, oe_vals=None, solr_vals=None, context=None):
        if not oe_vals:
            oe_vals = {}
        if not solr_vals:
            solr_vals = {}
        if field_type in ('char', 'text', 'integer', 'float') and oe_vals.get(field):
            solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
        elif field_type == 'boolean':
            solr_vals[self._solr_key(field_type)] = oe_vals.get(field)
        elif field_type == 'many2one' and oe_vals.get(field):
            val = oe_vals.get(field)
            obj = self.pool.get(relation)
            if isinstance(val, (list, tuple)):
                solr_vals["%s_i" % (field,)] = val[0]
                solr_vals["%s_s" % (field,)] = val[1]
            else:
                solr_vals["%s_i" % (field,)] = val
                val_name = obj.read(cr, uid, [val], [obj._rec_name], context=context)[0][obj._rec_name]
                solr_vals["%s_s" % (field,)] = val_name

            if field in included_relations:
                field_res_id = solr_vals["%s_i" % (field,)]
                new_vals = obj.read(cr, uid, [field_res_id], obj.fields_get(cr, uid, context=context).keys())[0]
                solr_values = obj.oe_to_solr(cr, uid, field_res_id, new_vals, field, context)
                for rel_k in solr_values.keys():
                    if rel_k != "id" and rel_k != "text":
                        solr_vals["%s_%s" % (field, rel_k)] = solr_values[rel_k]

        elif field_type in ('one2many', 'many2many') and oe_vals.get(field):
            obj = self.pool.get(relation)
            records = obj.read(cr, uid, oe_vals.get(field), [obj._rec_name], context=context)
            values = [r[obj._rec_name] for r in records]
            solr_vals["%s_sm" % (field,)] = values #TODO store ids?
        return solr_vals

    def oe_to_solr(self, cr, uid, res_id, oe_vals, parent, context=None):
        included_relations = self._get_included_relations(cr, uid, context)
        skipped_fields = self._get_skipped_fields(cr, uid, context)
        solr_vals = {}
        solr_vals["id"] = self._name.replace(".", "-") + "-" + str(res_id)
        solr_vals["text"] = oe_vals.get(self._rec_name)
        for field, descriptor in self.fields_get(cr, uid, context=context).iteritems():
            solr_vals = self._field_to_solr(cr, uid, field, descriptor['type'], descriptor.get('relation'), included_relations, oe_vals, solr_vals, context)
        return solr_vals

    def _urlencode(self, word):
        return unidecode(word).lower().strip().replace(".", "-").replace(" ", "-").replace("'", "-").replace(",", "").replace("--", "-").replace("---", "-")


class solr_collection_mixin(AbstractModel):
    _description='SolR Collection mixin'
    _name = 'solr.collection.mixin'
    _inherit = 'solr.mixin'
    _solr_collection_mixin = True

    def _solr_id(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = self._urlencode(item.name)
        return res

    _columns = {
        'solr_id': fields.function(_solr_id, string='ID SolR', type='char', store=True),
    }

    def create(self, cr, uid, values, context=None):
        res_id = super(solr_collection_mixin, self).create(cr, uid, values, context=context)
        si = self.pool.get('solr.config.settings').get_solr_interface(cr, uid, context)
        if si:
            solr_context = context.copy()
            solr_language_id = self.pool.get("ir.config_parameter").get_param(cr, uid, "solr.language_id", context=context)
            if solr_language_id:
                solr_context.update({'lang': self.pool.get('res.lang').read(cr, SUPERUSER_ID, [solr_language_id], ['iso_code'])[0]['iso_code']})
            new_vals = self.read(cr, uid, [res_id], self.fields_get(cr, uid, context=solr_context).keys(), context=solr_context)[0]
            solr_values = self.oe_to_solr(cr, uid, res_id, new_vals, False, context)
            si.add(solr_values)
            si.commit()
        return res_id

    def write(self, cr, uid, ids, values, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        si = self.pool.get('solr.config.settings').get_solr_interface(cr, uid, context)
        if si:
          si.delete([rec['solr_id'] for rec in self.read(cr, uid, ids, ['solr_id'])])
        res = super(solr_collection_mixin, self).write(cr, uid, ids, values, context=context)
        solr_context = False
        if si:
            for id in ids:
                if not solr_context:
                    solr_context = context and context.copy() or {}
                    solr_language_id = self.pool.get("ir.config_parameter").get_param(cr, uid, "solr.language_id", context=context)
                    if solr_language_id:
                        solr_context.update({'lang': self.pool.get('res.lang').read(cr, SUPERUSER_ID, [solr_language_id], ['iso_code'])[0]['iso_code']})
                new_vals = self.read(cr, uid, [id], self.fields_get(cr, uid, context=solr_context).keys(), context=solr_context)[0]
                solr_values = self.oe_to_solr(cr, uid, id, new_vals, False, context)
                si.add(solr_values)
                si.commit()
        return res

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        si = self.pool.get('solr.config.settings').get_solr_interface(cr, uid, context)
        if si:
          si.delete([rec['solr_id'] for rec in self.read(cr, uid, ids, ['solr_id'])])
        res = super(solr_collection_mixin, self).unlink(cr, uid, ids, context=context)
        return res
