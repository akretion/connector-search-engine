# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.backend import Backend
from openerp.addons.connector_nosql.backend import nosql


solr = Backend(parent=nosql)
""" Apache SolR Backend"""

solr3_4 = Backend(parent=solr, version='3-4')
""" Apache SolR 3 and 4"""
