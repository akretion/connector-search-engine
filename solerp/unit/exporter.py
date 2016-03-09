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
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Exporter
from ..connector import get_environment
from ..backend import solr
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


"""
Exporter for Apache Solr.
"""


@solr
class SolrExporter(Exporter):
    """ Base exporter for Apache Solr """
    __solr_pool = {}

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic exporter; how cool is that?

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SolrExporter, self).__init__(environment)
        self.bindings = None

    def _add(self, data):
        """ Create the SolR record """
        return self.backend_adapter.add(data)

    def run(self, binding_ids):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.bindings = self.model.browse(binding_ids)
        datas = []
        for binding in self.bindings:
            self.binding = binding
            map_record = self.mapper.map_record(binding)
            datas.append(map_record.values())
        return self._add(datas)


@job(default_channel='root.solr')
def export_record(session, model_name, binding_ids):
    # check that all binding believe to the same backend
    res = session.env[model_name].read_group(
        [('id', 'in', binding_ids)],
        ['id', 'backend_id'],
        ['backend_id'])
    if len(res) > 1:
        raise UserError('Binding do not believe to the same backend')
    env = get_environment(session, model_name, res[0]['backend_id'][0])
    exporter = env.get_connector_unit(SolrExporter)
    return exporter.run(binding_ids)
