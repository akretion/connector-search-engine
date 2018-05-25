# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class SeExporter(Component):
    _name = 'se.exporter'
    _inherit = ['base.se.connector', 'base.exporter']
    _usage = 'se.record.exporter'
    _base_mapper_usage = 'se.export.mapper'
    _base_backend_adapter_usage = 'se.backend.adapter'

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SeExporter, self).__init__(environment)
        self.bindings = None

    def _add(self, data):
        """ Create the SolR record """
        return self.backend_adapter.add(data)

    def _update(self, data):
        """
        Update data given in parameter
        :param data: list of dict
        :return:
        """
        return self.backend_adapter.update(data)

    def _export_data(self):
        return NotImplemented

    def run(self, records=None, mapper=None):
        """
        Run the synchronization (create or update).
        If some records are given in parameter, an update is done on them.
        Otherwise, a create is done for every records of the current work.
        :param records: recordset
        :param mapper: None or str
        :return:
        """
        # Load the mapper
        if not mapper:
            mapper = self.mapper
        else:
            mapper = self.component_by_name(mapper)
        # Default action is add
        action = self._add
        if records:
            action = self._update
        records = records or self.work.records
        datas = []
        lang = self.work.index.lang_id.code
        # Use the with_context only if necessary
        if records.env.context.get('lang', False) != lang:
            records = records.with_context(lang=lang)
        for record in records:
            map_record = mapper.map_record(record)
            datas.append(map_record.values())
        return action(datas)
