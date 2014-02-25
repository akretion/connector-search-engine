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
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.exception import IDMissingInBackend
from ..connector import get_environment

_logger = logging.getLogger(__name__)


"""
Exporters for Apache SolR.
"""

class SolRBaseExportSynchronizer(ExportSynchronizer):
    """ Base exporter for Apache SolR """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SolRBaseExportSynchronizer, self).__init__(environment)
        self.binding_id = None
        self.solr_id = None

    def _get_openerp_data(self):
        """ Return the raw OpenERP data for ``self.binding_id`` """
        return self.session.browse(self.model._name, self.binding_id)

    def run(self, binding_id, *args, **kwargs):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.binding_id = binding_id
        self.binding_record = self._get_openerp_data()
        result = self._run(*args, **kwargs)
        return result

    def _run(self):
        """ Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError


class SolRExportSynchronizer(SolRBaseExportSynchronizer):
    """ A common flow for the exports to SolR """

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

    def _map_data(self):
        """ Convert the external record to OpenERP """
        return self.mapper.map_record(self.binding_record)

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """ Create the SolR record """
        return self.backend_adapter.create(data)

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes"""
        assert self.binding_id
        assert self.binding_record

        map_record = self._map_data()
        record = self._create_data(map_record, fields=fields)
        si = SolrInterface(self.backend_record.location.encode('utf-8')) #TODO auth
        si.add(record)
        si.commit()
        return _('Record exported with ID %s on SolR.') % record['id']
