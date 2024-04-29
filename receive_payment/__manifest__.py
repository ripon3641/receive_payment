# -*- coding:utf-8 -*-

{
    'name': 'Receive Payment',
    'version': '16.0.0',
    'category': 'Accounting',
    'author': 'Ripon Hossain',
    'sequence': 1,
    'summary': 'Receive Payment Management',
    'description': "Receive Payment Management",
    'depends': ['mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menu.xml',
        'views/receive_payment.xml',
        'views/configurations.xml',
    ],
    'icon': ['static/icon.png'],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}
