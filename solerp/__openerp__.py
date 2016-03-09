{
    'name': 'SolR',
    'version': '0.1',
    'category': 'Connector',
    'summary': 'SolR',
    'description': """
SolR 

Features
--------

Sync objects to SolR

Schema
------

Solerp exports the OpenERP objects to match the SolR schema that is used
by Sunspot (a reference Ruby [on Rails] integration with SolR):
https://github.com/sunspot/sunspot/blob/master/sunspot_solr/solr/solr/conf/schema.xml
This also enables a better integration with Sunspot later in a Ruby web app.

Basically it relies a lot on dynamic fields so that SolR can
adapt to all OpenERP object definitions.

In a production system, you will likely still customize a lot your
schema.xml to provide more advanced search features. For instance you may
use a core with a specific schema for a given language, you may use
copyFields and advanced analysers...


Extension of Sunspot schema conventions to expose OpenERP associations in SolR
------------------------------------------------------------------------------

While complying with the Sunspot schema conventions, by default we
denormalize OpenERP data to SolR in such a way that we can reconstruct
the OpenERP associations around the exported object WITHOUT even hitting
OpenERP. That doesn't cost much performance and that was a requirement for
extreme speed and scalability in our project at Akretion.

**id**

First of all, unlike Sunspot, we support indexing multiple OpenERP databases in
a single SolR collection. It's doesn't cost much to support but it brings a
lot because a single SolR server can easily scale to many OpenERP instances.

So our id field is a bit different from the one from Sunspot. Sunspot stores
the object class along with the database record id.
Instead we store the OpenERP backend name, the OpenERP object name and the id.
Hence our id is guaranted to be unique, even with several OpenERP databases.

As SolR is flat NoSQL, it means we are using extra conventions on field names
to be able to reconstruct the associations when iterating over the field keys.
Most of the time the OpenERP "_rec_name" field is "name", but not always and
OpenERP is not exposing what it calls the object _rec_name in RPC by default so
we store it in the key names whenever required.

**m2o**

The Many To One associations got their id stored in field/id_its
And it get its description stored in field/{name}_ss where {name} is the name
of the field carrying the description in the related object (_recname)

**denormalized m2o**

A Many To One can be denormalized into the current flat SolR record.
For that, the containing object needs to have its _included_relations
listing the keys of the m2o associations you want to denormalize.
The denormalized data follows the same conventions describded here, except that
in the flat record, it's prefixed by {field}/ where field is the name of the m2o
field. This works recursively!

**o2m and m2m**

Only minimal information about o2m and m2m associations can be stored in a
falt SolR record using multivalued fields.

Usually it should be enough for indexing. But if it's not enough, eventually
you can consider indexing the object in the o2m and dernomalizing the former
object into it instead. Or you can also index several kind of OpenERP objects
into SolR and fake joins in your SolR app.

The ids of the o2m or m2m association are stored as: {field}/id_itms

If the description of the items is a text field, the different values are
stored in the same order in {field}/{name}_sms where name is the name of the
description field.

If instead the description of an item is carried by a m2o field, then
the ids are stored in {field}/{name}/{m2o-name}_sms where name is the rec_name
of the x2m field and m2o-name is the rec_name of the m2o field.


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
    'depends': ['connector_search_engine'],
    'data': [
        'solr_model_view.xml',
        'solr_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/backend_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
