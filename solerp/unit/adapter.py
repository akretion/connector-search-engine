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

from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from sunburnt import SolrInterface
from ..backend import solr


@solr
class SolrAdapter(BackendAdapter):
    _model_name = None

    __solr_pool = {}  # pool of connection for solr

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic exporter; how cool is that?

    def __init__(self, connector_env):
        self.location = connector_env.backend_record.location
        if not self.__solr_pool.get(self.location):
            self.__solr_pool[self.location] = SolrInterface(self.location)
        self.conn = self.__solr_pool[self.location]

    def add(self, datas):
        self.conn.add(datas, len(datas))
        self.conn.commit()

    def delete(self, binding_ids):
        self.conn.delete(binding_ids)
        self.conn.commit()
