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
from openerp.addons.connector_search_engine.unit.exporter import (
    SearchEngineExporter,
    export_record_search_engine,
    )
from ..connector import get_environment
from ..backend import solr
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


"""
Exporter for Apache Solr.
"""


@solr
class SolrExporter(SearchEngineExporter):
    """ Base exporter for Apache Solr """


@job(default_channel='root.solr')
def export_record(session, model_name, binding_ids):
    return export_record_search_engine(
        get_environment, session, model_name, binding_ids)
