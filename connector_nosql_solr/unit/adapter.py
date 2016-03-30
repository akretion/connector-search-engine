# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector_nosql.unit.adapter import NosqlAdapter
import sunburnt
from ..backend import solr


@solr
class SolrAdapter(NosqlAdapter):
    _model_name = None

    __solr_pool = {}  # pool of connection for solr

    def __init__(self, connector_env):
        location = connector_env.backend_record.location
        if not self.__solr_pool.get(location):
            self.__solr_pool[location] = sunburnt.SolrInterface(location)
        self.conn = self.__solr_pool[location]

    def add(self, datas):
        self.conn.add(datas, len(datas))
        self.conn.commit()

    def delete(self, binding_ids):
        self.conn.delete(binding_ids)
        self.conn.commit()
