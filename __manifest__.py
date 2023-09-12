{
    'name': 'Reporte de Utilidad',
    'version': '16.01',
    'description': ''' Reporte de utilidad exportable a XLS
    ''',
    'category': 'Stock',
    'author': 'IT Admin',
    'website': 'http://www.itadmin.com.mx',
    'depends': [
        'base','stock', 'account', 'point_of_sale','report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_utilidadpos_wizard.xml',
        'views/invoice_utilidadpos_id.xml',
        'views/pos_view.xml',
    ],
    'application': False,
    'installable': True,
}