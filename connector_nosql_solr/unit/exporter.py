# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from openerp.addons.connector.queue.job import job
from openerp.addons.connector_nosql.unit.exporter import export_record_nosql

_logger = logging.getLogger(__name__)


@job(default_channel='root.solr')
def export_record(session, model_name, binding_ids):
    return export_record_nosql(session, model_name, binding_ids)
