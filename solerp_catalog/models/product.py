# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, fields, models


class SolrProductTemplate(models.Model):
    _inherit = 'solr.binding'
    _name = 'solr.product.template'

    record_id = fields.Many2one('product.template')


class ProductTemplate(models.Model):
    _inherit='product.template'

    solr_bind_ids = fields.One2many(
        'solr.product.template',
        'record_id',
        string='Solr Binding')
