# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from sunburnt import SolrInterface
from openerp.tools.translate import _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Deleter
from openerp.addons.connector_nosql.connector import get_environment
from ..backend import solr


# TODO we could have a batch mode too like the exporter eventually
@solr
class SolrDeleter(Deleter):
    """ Base deleter for Solr """

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic deleter; how cool is that?

    def run(self, solr_id):
        """ Run the synchronization, delete the record on Solr
        :param solr_id: identifier of the record to delete
        """
        si = SolrInterface(self.backend_record.location.encode('utf-8'))
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
        deleter = env.get_connector_unit(SolRDeleter)
        solr_id = "%s %s %s" % (backend.name, model_name, record_id)
        res = deleter.run(solr_id)
    return res
