# This is an example configuration file to export products on SolR
# you can include it in the __init__.py and also add the dependency upon the 'product' module in __openerp__.py to test it.
# of course, you would usually define such configuration in custom modules.

from openerp.addons.connector.event import on_record_create, on_record_write, on_record_unlink
from .unit.export_synchronizer import export_record
from .unit.delete_synchronizer import export_delete_record

@on_record_write(model_names='product.product')
def solr_product_modified(session, model_name, record_id, vals):
    export_record.delay(session, model_name, record_id)

@on_record_create(model_names='product.product')
def solr_product_modified(session, model_name, record_id, vals):
    export_record.delay(session, model_name, record_id)

@on_record_unlink(model_names='product.product')
def delay_unlink(session, model_name, record_id):
    export_delete_record.delay(session, model_name, record_id)
