# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Raphaël Valyi
#    Copyright 2013 Akretion LTDA
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

import time
import logging
from datetime import datetime
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.queue.job import job
import openerp.addons.connector as connector
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper
                                                  )
from .backend import solr

_logger = logging.getLogger(__name__)


class solr_backend(orm.Model):
    _name = 'solr.backend'
    _description = 'Apache SolR Backend'
    _inherit = 'connector.backend'
    _backend_type = 'solr'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('3-4', '3-4')]

    _columns = {
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True),
        'location': fields.char('Location', required=True),
        'username': fields.char('Username'),
        'password': fields.char('Password'),
        'default_lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language."),
        'export_ids': fields.many2many('ir.exports', 'solr_backend_ir_exports_rel', 'backend_id', 'export_id', 'Exports', help="Associate here the exports to this Solr backend"),
    }

    def index_all(self, cr, uid, ids, context=None):
        import product #TODO don't import example
        session = ConnectorSession(cr,uid,context)
        product_obj = self.pool.get('product.product')
        p_ids = product_obj.search(cr, uid, [], context=context)
#        p_ids = product_obj.search(cr, uid, [['id', '<', 34962], ['id', '>', '14000']], context=context)
        c = 0
        for i in p_ids:
            _logger.info(i)
            product.export_record.delay(session, 'product.product', i, commit=False) #TODO loop over objects listed in backend (or having new mixin TODO)
            c += 1
            if c > 500:
                cr.commit()
                c = 0

    def output_recorder(self, cr, uid, ids, context=None):
        """ Utility method to output a file containing all the recorded
        requests / responses with Solr.  Used to generate test data.
        Should be called with ``erppeek`` for instance.
        """
        from .unit.backend_adapter import output_recorder
        import os
        import tempfile
        fmt = '%Y-%m-%d-%H-%M-%S'
        timestamp = datetime.now().strftime(fmt)
        filename = 'output_%s_%s' % (cr.dbname, timestamp)
        path = os.path.join(tempfile.gettempdir(), filename)
        output_recorder(path)
        return path
