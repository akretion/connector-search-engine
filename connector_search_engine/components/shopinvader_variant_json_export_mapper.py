# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopinvaderVariantJsonExportMapper(Component):
    """
    Define a default shopinvader.variant json export mapper
    """
    _name = 'shopinvader.variant.json.export.mapper'
    _inherit = 'json.export.mapper'
    _apply_on = ['shopinvader.variant']
