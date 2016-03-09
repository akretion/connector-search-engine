# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014 Akretion (http://www.akretion.com/)
#    @author: Raphaël Valyi <raphael.valyi@akretion.com>
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

from openerp.addons.connector_search_engine.unit.adapter import\
    SearchEngineAdapter
import sunburnt
from ..backend import solr


@solr
class SolrAdapter(SearchEngineAdapter):
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
