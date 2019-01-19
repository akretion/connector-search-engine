# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
import json

from odoo.addons.component.core import Component
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


try:
    import algoliasearch
except ImportError:
    _logger.debug('Can not import algoliasearch')


class AlgoliaAdapter(Component):
    _name = "algolia.adapter"
    _inherit = ['base.backend.adapter', 'algolia.se.connector']
    _usage = 'se.backend.adapter'

    def _get_index(self):
        backend = self.backend_record
        account = backend._get_existing_keychain()
        client = algoliasearch.client.Client(
            backend.algolia_app_id, account._get_password())
        return client.initIndex(self.work.index.name)

    def set_settings(self, force=True):
        """Set advanced settings like facettings attributes."""
        set_settings = force
        index = self._get_index()
        data = self.work.index._get_setting_values()
        if not force:
            # TODO check if index exist in order to know if we should export
            # setting
            pass
        if data and set_settings:
            index.setSettings(data)

    def index(self, datas):
        index = self._get_index()
        # Ensure that the objectID is set because algolia will use it
        # for creating or updating the record
        for data in datas:
            if not data.get('objectID'):
                raise UserError(
                    _('The key objectID is missing in the data %s') % data)
        index.add_objects(datas)

    def delete(self, binding_ids):
        index = self._get_index()
        index.delete_objects(binding_ids)

    def clear(self):
        index = self._get_index()
        index.clear_index()
        self.set_settings()
