import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-akretion-connector-search-engine",
    description="Meta package for akretion-connector-search-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-connector_algolia',
        'odoo8-addon-connector_search_engine',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
