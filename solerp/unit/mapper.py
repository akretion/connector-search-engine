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

from unidecode import unidecode
from openerp.tools.translate import _
from openerp.addons.connector.unit.mapper import (
    mapping,
    ExportMapper
)
from ..backend import solr

def solr_key(field_type):
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


class SolRExportMapper(ExportMapper):

    def _get_included_relations(self, record):
        return []

    def _get_skipped_fields(self, record):
        return []

    def _solr_key(self, field_type):
        return solr_key(field_type)

    def _field_to_solr(self, field, field_type, relation, included_relations, oe_vals=None, solr_vals=None):
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
            obj = self.session.pool[relation]
            if isinstance(val, (list, tuple)):
                solr_vals["%s_i" % (field,)] = val[0]
                solr_vals["%s_s" % (field,)] = val[1]
            else:
                solr_vals["%s_i" % (field,)] = val
                val_name = obj.read(cr, uid, [val], [obj._rec_name], context=self.session.context)[0][obj._rec_name]
                solr_vals["%s_s" % (field,)] = val_name

            if field in included_relations:
                field_res_id = solr_vals["%s_i" % (field,)]
                included_record = obj.browse(self.session.cr, self.session.uid, field_res_id, context=self.session.context)
                solr_values = self._oe_to_solr(included_record) #TODO find object specific Mapper ?
                for rel_k in solr_values.keys():
                    if rel_k != "id" and rel_k != "text":
                        solr_vals["%s_%s" % (field, rel_k)] = solr_values[rel_k]

        elif field_type in ('one2many', 'many2many') and oe_vals.get(field):
            obj = self.session.pool.get(relation)
            records = obj.read(self.session.cr, self.session.uid, oe_vals.get(field), [obj._rec_name], context=self.session.context)
            values = [r[obj._rec_name] for r in records]
            solr_vals["%s_sm" % (field,)] = values #TODO store ids?
        return solr_vals

    def oe_to_solr(self, record, fields=None):
        return self._oe_to_solr(record, fields)

    def _oe_to_solr(self, record, fields=None):
        model = record._model
        fields_dict = model.fields_get(self.session.cr, self.session.uid, context=self.session.context)
        oe_vals = model.read(self.session.cr, self.session.uid, [record.id], fields_dict.keys(), context=self.session.context)[0]
        included_relations = self._get_included_relations(record)
        skipped_fields = self._get_skipped_fields(record) #TODO use them + refactor
        solr_vals = {}
        solr_vals["id"] = "%s-%s" % (self.backend_record.name, record.id)
        solr_vals["slug_s"] = self._slug(record)
        solr_vals["object_s"] = model._name
        solr_vals["text"] = oe_vals.get(model._rec_name) #TODO change or remove?
        for field, descriptor in fields_dict.iteritems():
            solr_vals = self._field_to_solr(field, descriptor['type'], descriptor.get('relation'), included_relations, oe_vals, solr_vals)
        return solr_vals

    def _urlencode(self, word):
        return unidecode(word).lower().strip().replace(".", "-").replace(" ", "-").replace("'", "-").replace(",", "").replace("--", "-").replace("---", "-").replace("/", "-").replace("&", "e")

    def _slug_parts(self, record):
        raw_name = getattr(record, record._model._rec_name)
        name = self._urlencode(raw_name)
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
