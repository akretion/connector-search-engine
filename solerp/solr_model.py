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

import logging
from datetime import datetime
from openerp import fields, models

_logger = logging.getLogger(__name__)


class SolrBackend(models.Model):
    _name = 'solr.backend'
    _description = 'Apache SolR Backend'
    _inherit = 'connector.backend'
    _backend_type = 'solr'

    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('3-4', '3-4')]

    version = fields.Selection(
        '_select_versions',
        required=True)
    location = fields.Char(required=True)
    username = fields.Char()
    password = fields.Char()
    default_lang_id = fields.Many2one(
        'res.lang',
        'Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.")

    def output_recorder(self):
        """ Utility method to output a file containing all the recorded
        requests / responses with Solr.  Used to generate test data.
        Should be called with ``erppeek`` for instance.
        """
        from .unit.backend_adapter import output_recorder
        import os
        import tempfile
        fmt = '%Y-%m-%d-%H-%M-%S'
        timestamp = datetime.now().strftime(fmt)
        filename = 'output_%s_%s' % (self._cr.dbname, timestamp)
        path = os.path.join(tempfile.gettempdir(), filename)
        output_recorder(path)
        return path


class SolrBinding(models.AbstractModel):
    _inherit = 'batch.binding'
    _name = 'solr.binding'

    backend_id = fields.Many2one('solr.backend')
