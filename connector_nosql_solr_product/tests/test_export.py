# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_nosql_solr.tests.common import (
    mock_api,
    SetUpSolrBase,
)
from openerp.addons.connector.tests.common import mock_job_delay_to_direct
from . import data_export


class ExportProduct(SetUpSolrBase):

    def test_export_product(self):
        path =\
            'openerp.addons.connector_nosql_solr.unit.exporter.export_record'
        for xml_id in (3, 4):
            tmpl = self.env.ref(
                'product.product_product_%s_product_template' % xml_id)
            self.env['nosql.product.template'].create({
                'backend_id': self.backend.id,
                'record_id': tmpl.id,
                })
        with mock_job_delay_to_direct(path), mock_api() as API:
            self.env['nosql.backend']._scheduler_export_product()
            for item in API._calls[0][2]:
                for key in [
                        'write_date_dts',
                        'create_date_dts',
                        '__last_update_dts',
                        'display_name_ss',
                        'id',
                        'id_is',
                        'record_id/id_is']:
                    item.pop(key)
            self.assertEqual(API._calls, data_export.export_product_3_4)
