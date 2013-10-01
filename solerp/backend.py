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

import openerp.addons.connector.backend as backend


solr = backend.Backend('solr')
""" Generic Apache SolR Backend """

solr3_4 = backend.Backend(parent=solr, version='3-4')
""" Apache SolR 3 and 4"""

