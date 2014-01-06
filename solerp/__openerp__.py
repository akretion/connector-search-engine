{
    'name': 'SolR',
    'version': '0.1',
    'category': 'Connector',
    'summary': 'SolR',
    'description': """
SolR 

features
--------

Sync objects to SolR

schema
------

Solerp exports the OpenERP objects to match the SolR schema that is used
by Sunspot (a reference Ruby [on Rails] integration with SolR):
https://github.com/sunspot/sunspot/blob/master/sunspot_solr/solr/solr/conf/schema.xml
This also enables a better integration with Sunspot later in a Ruby web app.

Basically it relies a lot on dynamic fields so that SolR can
adapt to all OpenERP object definitions.

In a production system, you will instead likely customize a lot your
schema.xml to provide more advanced search features.


supported objects
-----------------

Any OpenERP object can be synch'ed.
But this module comes with a demo for product.product.
To test it, just uncomment "import product" in __init__.py

In a production system, you will instead probably implement your own
export logic or overrides object by objects in some custom modules.


    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'images': [],
    'depends': ['connector'],
    'data': ['solr_model_view.xml', 'solr_menu.xml', 'security/ir.model.access.csv'],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
