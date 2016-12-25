# -*- coding: utf-8 -*-
##############################################################################
#
#	Importar datos de BD de Dentaltix en OpenERP 7
#
##############################################################################

{
	'name': 'Dentaltix - Importar información desde OpenERP 7',
	'summary': 'Importar información desde OpenERP 7',
	'version': '0.1',
	'category': 'Extra Tools',
	'author': '@MarcoGonzalo',
    "license": "AGPL-3",
    "application": False,
	'installable': True,
	'description': """	
		Cambio a readonly=False para exportar campos de sale.order, account.invoice, y otros importantes
	""",
	'depends': [
		'account', 'res.partner', 'sale'
	],
	'data': [
	],
}