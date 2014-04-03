# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Akretion (http://www.akretion.com/)
#    @author: Raphaël Valyi <raphael.valyi@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from slugify import slugify

from openerp import tools
from openerp.tools.translate import _
from openerp.addons.connector.unit.mapper import (
    mapping,
    ExportMapper
)
from ..backend import solr

import logging

_logger = logging.getLogger(__name__)

def solr_key(field_type):
    """ modeled after Sunspot dynamic fields: https://github.com/sunspot/sunspot/blob/master/sunspot_solr/solr/solr/conf/schema.xml """
    return {
            'selection': "%s_s",
            'char': "%s_s", # use copyField to text in your schema if you need to
            'text': "%s_s",
            'integer': "%s_i",
            'date': "%s_d",
            'datetime': "%s_dt",
            'float': "%s_f",
            'boolean': "%s_b",
            'many2one': "%s_s",
            'one2many': "%s_sm",
            'many2many': "%s_sm",
            'binary': "%s_64", # NOTE not coming from Sunspot,
                               # don't forget to add it in your schema
                               # if you use the _export_binaries flag
    }.get(field_type, "%s_s")


@solr
class SolRExportMapper(ExportMapper):
    _export_binaries = False
    _export_functions = False

    @classmethod
    def match(cls, session, model):
        return True #We are a generic mapper; how cool is that?

    layout = (
# example of fields/associations layout DSL as follow:
# TODO offer a way to build it from a custom ir_exports
#        '+include_field',
#        '-skip_field',
#        'only_field',
#        'only_field2-custom_sufix' #custom Solr dynamic field suffix, after hyphen; can be with include field too #TODO use custom suffix!
#        ('categ_id', ()), #all
#        ('uom_id', ()),
#        ('image_ids', ('url',)) #only url
    )

    def _solr_key(self, field_type, multiple=False):
        if multiple:
            return "%sms" % (solr_key(field_type),)
        else:
            return "%ss" % (solr_key(field_type),) #TODO only add s if field is stored

    def _field_to_solr(self, field, field_type, relation, oe_vals=None, solr_vals=None, field_layout=None):
        if not oe_vals:
            oe_vals = {}
        if not solr_vals:
            solr_vals = {}

        if field_type == 'many2one' and oe_vals.get(field):
            val = oe_vals.get(field)
            obj = self.session.pool[relation]
            if isinstance(val, (list, tuple)):
                solr_vals["%s/id_is" % (field,)] = val[0]
                solr_vals["%s/%s_ss" % (field, obj._rec_name)] = val[1]
            else:
                solr_vals["%s/id_is" % (field,)] = val
                val_name = obj.read(cr, uid, [val], [obj._rec_name], context=self.session.context)[0][obj._rec_name]
                solr_vals["%s/%s_ss" % (field, obj._rec_name)] = val_name

            if field_layout is not None:
                field_res_id = solr_vals["%s/id_is" % (field,)]
                included_record = obj.browse(self.session.cr, self.session.uid, field_res_id, context=self.session.context)
                solr_values = self._oe_to_solr(included_record, oe_vals, field_layout) #TODO find object specific Mapper ?
                for rel_k in solr_values.keys():
                     solr_vals["%s/%s" % (field, rel_k)] = solr_values[rel_k]

        elif field_type in ('one2many', 'many2many') and oe_vals.get(field):
            obj = self.session.pool.get(relation)
            if field_layout:
                x2m_fields = [self.norm(i) for i in field_layout] + [obj._rec_name]
                x2m_fields_dict = obj.fields_get(self.session.cr, self.session.uid, allfields=x2m_fields, context=self.session.context)
            else:
                x2m_fields = [obj._rec_name]
                x2m_fields_dict = obj.fields_get(self.session.cr, self.session.uid, allfields=x2m_fields, context=self.session.context)
            records = obj.read(self.session.cr, self.session.uid, oe_vals.get(field), x2m_fields, context=self.session.context)
            ids = []
            flat_vals = []
            m2o_vals = []
            m2o_ids = []
            extra_vals = {}
            for r in records:
                ids.append(r['id'])
                rec_name = r[obj._rec_name]
                if isinstance(rec_name, (list, tuple)): # rec_name is (id, name) of a m2o
                    m2o_ids.append(rec_name[0])
                    m2o_vals.append(rec_name[1])
                else:
                    flat_vals.append(rec_name)
                for i in x2m_fields:
                    if extra_vals.get(i):
                        extra_vals[i].append(r[i])
                    else:
                        extra_vals[i] = [r[i]]
            solr_vals["%s/id_ims" % (field,)] = ids
            if flat_vals:
                solr_vals["%s/%s_sms" % (field, obj._rec_name)] = flat_vals
            else:
                solr_vals["%s/%s/%s_sms" % (field, obj._rec_name, "name")] = m2o_vals #FIXME shouldn't be hardcoded
                solr_vals["%s/%s/id_ims" % (field, obj._rec_name)] = m2o_ids
            for i in x2m_fields:
                f_type = x2m_fields_dict[i]['type']
                sub_key = self._solr_key(f_type, True) % (i,)
                if f_type == 'many2one':
                    vals = [t[1] for t in extra_vals[i]]
                else:
                    vals = extra_vals[i]
                solr_vals["%s/%s" % (field, sub_key)] = vals

        elif field_type == 'binary' and self._export_binaries and oe_vals.get(field):
            solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
        elif field_type not in ('binary', 'serialized'):
            if field_type == 'boolean':
                solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
            elif oe_vals.get(field):
                if field_layout:
                    solr_vals[field_layout.replace('-', '_')] = oe_vals.get(field)
                else:
                    solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
        return solr_vals

    def norm(self, item):
        if type(item) == str:
            return item.replace('-', '').replace('+', '').split('-')[0]
        elif type(item) in (list, tuple):
            return self.norm(item[0])

    @tools.ormcache() #TODO invalid that cache when changing a model def? (for now just restart)
    def _get_fields(self, model, layout):
        if layout is None:
            layout = []
        only = [self.norm(i) for i in layout if type(i) == str and '+' not in i and '-' not in i]
        include = [self.norm(i) for i in layout if type(i) == str and '+' in i]
        skip = [self.norm(i) for i in layout if type(i) == str and '-' in i]
        if only:
            fields = only
            fields_dict = model.fields_get(self.session.cr, self.session.uid, allfields=fields, context=self.session.context)
        else:
            fields_dict = model.fields_get(self.session.cr, self.session.uid, context=self.session.context)
            fields = fields_dict.keys()
        export_fields = []
        for k in fields:
            descriptor = fields_dict[k]
            if descriptor.get('function'):
                if descriptor.get('store') or k.startswith('x_'):
                    export_fields.append(k)
                elif self._export_functions or k in include:
                    export_fields.append(k)
            elif k not in skip:
                export_fields.append(k)
        return fields_dict, export_fields

    def _oe_to_solr(self, record, parent_vals=None, layout=None):
        model = record._model
        fields_dict, fields = self._get_fields(model, layout)
        oe_vals = model.read(self.session.cr, self.session.uid, [record.id], fields, context=self.session.context)[0]
        # NOTE pre-read records by chunks of several ids to optimize?
        #TODO allow to have indexed fields not stored, read that in ir.fields eventually + cache that in the session
        solr_vals = {}
        if not parent_vals:
            solr_vals["id"] = "%s %s %s" % (self.backend_record.name, model._name, record.id)
            solr_vals["slug_ss"] = self._slug(record)
            solr_vals["instance_ss"] = self.backend_record.name
            solr_vals["text"] = oe_vals.get(model._rec_name) #TODO change or remove?
            solr_vals["type"] = model._name.title().replace('.', '')
        for field in fields:
            descriptor = fields_dict[field]
            field_layout = None
            for i in layout: #TODO implement + / - to add / remove fields
                if type(i) in (list, tuple) and i[0].replace('+', '').replace('-', '') == field:
                    field_layout = i[1]
                    break
                elif ("%s-" % (field,)) in i: #custom_suffix
                    field_layout = i
            solr_vals = self._field_to_solr(field, descriptor['type'], descriptor.get('relation'), oe_vals, solr_vals, field_layout)
        return solr_vals

    def _slug_parts(self, record):
        raw_name = getattr(record, record._model._rec_name)
        name = slugify(raw_name)
        parts = [record._model._name.replace(".", "-"), name]
        search = record._model.search(self.session.cr, self.session.uid, [[record._model._rec_name, '=', raw_name]])
        if search and search[0] != record.id:
            parts += [str(record.id)]
        return parts

    def _slug(self, record): #NOTE in an SEO/web prospective, mais SolR id is a name instead of of the OpenERP id
        return "/".join(self._slug_parts(record))

    def finalize(self, map_record, values):
        """ Called at the end of the mapping.

        Can be used to modify the values before returning them, as the
        ``on_change``.

        :param map_record: source map_record
        :type map_record: :py:class:`MapRecord`
        :param values: mapped values
        :returns: mapped values
        :rtype: dict
        """
        return self._oe_to_solr(map_record._source, None, self.layout)
