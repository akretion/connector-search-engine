# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_search_engine.connector import get_environment
from ..unit.adapter import AlgoliaAdapter
import logging
_logger = logging.getLogger(__name__)


class SeBackend(models.Model):
    _inherit = 'se.backend'

    version = fields.Selection(selection_add=[('algolia_v1', 'Algolia V1')])
    algolia_app_id = fields.Char(sparse="data", string="APP ID")
    algolia_api_key = fields.Char(related='password', string="API KEY")


class SeIndex(models.Model):
    _inherit = 'se.index'

    @api.model
    def clear_all_index_dead_content(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).clear_dead_content()

    @api.multi
    def _clear_dead_resource(self, adapter, res):
        model_obj = self.env[self.model_id.model]
        delete_ids = []
        for hit in res['hits']:
            record = model_obj.search([
                ('record_id', '=', int(hit['objectID'])),
                ])
            if not record:
               delete_ids.append(hit['objectID'])
        if delete_ids:
            _logger.info(
                "Drop dead content for index %s objectID %s",
                record.name, delete_ids)
            adapter.delete(delete_ids)

    @api.multi
    def clear_dead_content(self):
        for index in self:
            session = ConnectorSession(self._cr, self._uid, self._context)
            env = get_environment(session, self._name, index.id)
            adapter = env.get_connector_unit(AlgoliaAdapter)
            res = adapter.browse_from({"query": ""}, None)
            index._clear_dead_resource(adapter, res)
            while "cursor" in res:
                res = adapter.browse_from(None, res["cursor"])
                index._clear_dead_resource(adapter, res)
