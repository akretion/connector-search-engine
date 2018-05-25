# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Connector Search Engine Algolia stock",
    "summary": "Shopinvader stock algolia",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion,ACSONE SA/NV",
    "license": "AGPL-3",
    "depends": [
        'stock',
        'shopinvader',
        'connector_search_engine',
        'connector_search_engine_stock',
        'shopinvader_algolia',
    ],
    "data": [
        'views/se_backend_algolia.xml',
    ],
}
