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

from sunburnt import SolrInterface
from openerp.tools.translate import _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import DeleteSynchronizer
from ..connector import get_environment


class SolRDeleteSynchronizer(DeleteSynchronizer):
    """ Base deleter for SolR """

    def run(self, solr_id):
        """ Run the synchronization, delete the record on SolR
        :param solr_id: identifier of the record to delete
        """
        si = SolrInterface(self.backend_record.location) #TODO auth
        si.delete(solr_id)
        return _('Record %s deleted on SolR') % solr_id
