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
            'text': "%s_text",
            'integer': "%s_it",
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


class SolRExportMapper(ExportMapper):
    _export_binaries = False
    _export_functions = False
    _only_fields = []
    _skip_fields = []
    _included_relations = []

    def _get_included_relations(self, record):
        return self._included_relations

    def _solr_key(self, field_type):
        return "%ss" % (solr_key(field_type),) #TODO only add s if field is stored

    def _field_to_solr(self, field, field_type, relation, included_relations, oe_vals=None, solr_vals=None):
        if not oe_vals:
            oe_vals = {}
        if not solr_vals:
            solr_vals = {}

        if field_type == 'many2one' and oe_vals.get(field):
            val = oe_vals.get(field)
            obj = self.session.pool[relation]
            if isinstance(val, (list, tuple)):
                solr_vals["%s_its" % (field,)] = val[0]
                solr_vals["%s-%s-m2o_ss" % (field, obj._rec_name)] = val[1]
            else:
                solr_vals["%s_its" % (field,)] = val
                val_name = obj.read(cr, uid, [val], [obj._rec_name], context=self.session.context)[0][obj._rec_name]
                solr_vals["%s-%s-m2o_ss" % (field, obj._rec_name)] = val_name

            if field in included_relations:
                field_res_id = solr_vals["%s_its" % (field,)]
                included_record = obj.browse(self.session.cr, self.session.uid, field_res_id, context=self.session.context)
                solr_values = self._oe_to_solr(included_record, None, oe_vals) #TODO find object specific Mapper ?
                for rel_k in solr_values.keys():
#                    if rel_k not in ["id", "slug_ss", "text", "class_name", "instance_s", "type"]:
                     solr_vals["%s/%s" % (field, rel_k)] = solr_values[rel_k]

        elif field_type in ('one2many', 'many2many') and oe_vals.get(field):
            obj = self.session.pool.get(relation)
            records = obj.read(self.session.cr, self.session.uid, oe_vals.get(field), [obj._rec_name], context=self.session.context)
            ids = []
            flat_vals = []
            m2o_vals = []
            m2o_ids = []
            for r in records:
                ids.append(r['id'])
                rec_name = r[obj._rec_name]
                if isinstance(rec_name, (list, tuple)): # rec_name is (id, name) of a m2o
                    m2o_ids.append(rec_name[0])
                    m2o_vals.append(rec_name[1])
                else:
                    flat_vals.append(rec_name)
            solr_vals["%s_itms" % (field,)] = ids
            if field_type == 'one2many':
                rel = "o2m"
            else:
                rel = "m2m"
            if flat_vals:
                solr_vals["%s-%s-%s_sms" % (field, obj._rec_name, rel)] = flat_vals
            else:
                solr_vals["%s-%s-%s-m2o_sms" % (field, obj._rec_name, rel)] = m2o_vals 
                solr_vals["%s-%s-%s-m2o_itms" % (field, obj._rec_name, rel)] = m2o_ids

        elif field_type == 'binary' and self._export_binaries and oe_vals.get(field):
            solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
        elif field_type != 'binary':
            if field_type == 'boolean':
                solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
            elif oe_vals.get(field):
                solr_vals[self._solr_key(field_type) % (field, )] = oe_vals.get(field)
        return solr_vals

    def oe_to_solr(self, record, fields=None):
        return self._oe_to_solr(record, fields)

    def _get_fields(self, model):
        if self._only_fields:
            fields = self._only_fields
            fields_dict = model.fields_get(self.session.cr, self.session.uid, allfields=fields, context=self.session.context)
        else:
            fields_dict = model.fields_get(self.session.cr, self.session.uid, context=self.session.context)
            fields = fields_dict.keys()
        fields = [k for k in fields if k not in self._skip_fields]
        return fields_dict, fields

    def _oe_to_solr(self, record, changed_fields=None, parent_vals=None):
        model = record._model
        fields_dict, fields = self._get_fields(model)
        oe_vals = model.read(self.session.cr, self.session.uid, [record.id], fields, context=self.session.context)[0]
        # NOTE pre-read records by chunks of several ids to optimize?
        included_relations = self._get_included_relations(record)
        #TODO allow to have indexed fields not stored, read that in ir.fields eventually + cache that in the session
        solr_vals = {}
        if not parent_vals:
            solr_vals["id"] = "%s %s %s" % (self.backend_record.name, model._name, record.id)
            solr_vals["slug_ss"] = self._slug(record)
            solr_vals["class_name"] = model._name
            solr_vals["instance_ss"] = self.backend_record.name
            solr_vals["text"] = oe_vals.get(model._rec_name) #TODO change or remove?
            solr_vals["type"] = model._name.title().replace('.', '')
        for field in fields:
            descriptor = fields_dict[field]
            if descriptor.get('function') and not descriptor.get('store') and not self._export_functions:
                continue
            solr_vals = self._field_to_solr(field, descriptor['type'], descriptor.get('relation'), included_relations, oe_vals, solr_vals)
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

    def convert(self, record, fields=None):
        self._convert(record, fields)
        self._data.update(self.oe_to_solr(record, fields))
