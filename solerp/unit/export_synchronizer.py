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
from sunburnt import SolrInterface
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.exception import IDMissingInBackend
from ..connector import get_environment
from ..backend import solr

_logger = logging.getLogger(__name__)


"""
Exporter for Apache Solr.
"""

NUMBER_OF_DOCS_PER_ADD = 50
NUMBER_OF_DOCS_PER_COMMIT = 1000


@solr
class SolrExporter(Exporter):
    """ Base exporter for Apache Solr """
    __solr_pool = {}

    @classmethod
    def match(cls, session, model):
        return True #We are a generic exporter; how cool is that?

    @classmethod
    def add(self, url, doc):
        si_item = self.__solr_pool.get(url)
        if not si_item:
            si_item = [SolrInterface(url), 0, []]
            self.__solr_pool[url] = si_item
        si_item[2].append(doc)
        si_item[1] += 1
        if si_item[1] % NUMBER_OF_DOCS_PER_ADD == 0: # NOTE: Solr itself will also auto-commit after some time
           si_item[0].add(si_item[2])
           si_item[2] = []
        if si_item[1] > NUMBER_OF_DOCS_PER_COMMIT:
            si_item[0].commit()
            si_item[1] = 0
        return _('Record exported with ID %s on SolR.') % doc['id']

    @classmethod
    def commit(self, url):
        si_item = self.__solr_pool.get(url)
        if si_item:
            si_item[0].add(si_item[2])
            si_item[2] = []
            si_item[0].commit()

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SolRExportSynchronizer, self).__init__(environment)
        self.binding_record = None

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return False

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """ Create the SolR record """
        return self.backend_adapter.create(data)


    def run(self, binding_id, *args, **kwargs):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.binding_id = binding_id
        self.binding_record = self.session.browse(kwargs['model_name'], self.binding_id)
        del kwargs['model_name']
        map_record = self.mapper.map_record(self.binding_record)
#        map_record = self._map_data()
        record = self._create_data(map_record, **kwargs)
        return SolRExportSynchronizer.add(self.backend_record.location.encode('utf-8'), record)


@job
def export_record(session, model_name, record_id, commit=True, fields=None):
    res = False
    for backend_id in session.search('solr.backend', []):
        env = get_environment(session, model_name, backend_id)
        exporter = env.get_connector_unit(SolRExportSynchronizer)
        res = exporter.run(record_id, fields=fields, model_name=model_name)
        if commit:
            SolRExportSynchronizer.commit(exporter.backend_record.location.encode('utf-8'))
    return res
