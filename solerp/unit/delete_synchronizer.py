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
from openerp.addons.connector.unit.synchronizer import Deleter
from ..connector import get_environment
from ..backend import solr


#TODO we could have a batch mode too like the exporter eventually
@solr
class SolrDeleter(Deleter):
    """ Base deleter for Solr """

    @classmethod
    def match(cls, session, model):
        return True #We are a generic deleter; how cool is that?

    def run(self, solr_id):
        """ Run the synchronization, delete the record on Solr
        :param solr_id: identifier of the record to delete
        """
        si = SolrInterface(self.backend_record.location.encode('utf-8')) #TODO auth
        si.delete(solr_id)
        si.commit()
        return _('Record %s deleted on Solr') % solr_id


@job
def export_delete_record(session, model_name, record_id):
    """ Delete a record on Solr """
    res = False
    backend_ids = session.search('solr.backend', [])
    for backend in session.browse('solr.backend', backend_ids):
        env = get_environment(session, model_name, backend.id)
        deleter = env.get_connector_unit(SolRDeleteSynchronizer)
        solr_id = "%s %s %s" % (backend.name, model_name, record_id)
        res = deleter.run(solr_id)
    return res
