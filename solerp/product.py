# This is an example configuration file to export products on SolR
# you can include it in the __init__.py and also add the dependency upon the 'product' module in __openerp__.py to test it.
# of course, you would usually define such configuration in custom modules.


import sunburnt
from unidecode import unidecode
from operator import itemgetter
from openerp.osv.orm import Model, TransientModel, AbstractModel
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.event import on_record_create, on_record_write, on_record_unlink
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.exception import (MappingError,
                                                InvalidDataError,
                                                IDMissingInBackend)
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  )
from .connector import get_environment
from .backend import solr
from .unit.export_synchronizer import SolRExportSynchronizer
from .unit.delete_synchronizer import SolRDeleteSynchronizer
from .unit.mapper import SolRExportMapper

@solr
class ProductExporter(SolRExportSynchronizer):
    _model_name = ['product.product']

@solr
class ProductDeleter(SolRDeleteSynchronizer):
    _model_name = ['product.product']

@solr
class ProductExportMapper(SolRExportMapper):
   _model_name = ['product.product']

@on_record_write(model_names='product.product')
def solr_product_modified(session, model_name, record_id, fields=None):
    export_record.delay(session, model_name, record_id, fields=fields, priority=20)

@on_record_create(model_names='product.product')
def solr_product_modified(session, model_name, record_id, fields=None):
    export_record.delay(session, model_name, record_id, fields=fields, priority=20)

@on_record_unlink(model_names='product.product')
def delay_unlink(session, model_name, record_id):
    export_delete_record.delay(session, model_name, record_id)

@job
def export_record(session, model_name, record_id, fields=None):
    res = False
    for backend_id in session.search('solr.backend', []):
        env = get_environment(session, model_name, backend_id)
        exporter = env.get_connector_unit(ProductExporter)
        res = exporter.run(record_id, fields)
    return res

@job
def export_delete_record(session, model_name, record_id):
    """ Delete a record on SolR """
    res = False
    backend_ids = session.search('solr.backend', [])
    for backend in session.browse('solr.backend', backend_ids):
        env = get_environment(session, model_name, backend.id)
        deleter = env.get_connector_unit(ProductDeleter)
        solr_id = "%s-%s" % (backend.name, record_id)
        res = deleter.run(solr_id)
    return res

