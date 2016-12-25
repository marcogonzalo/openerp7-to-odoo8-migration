# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

import psycopg2

# Connection to the source database
src_db = psycopg2.connect(host="ramon.bitnamiapp.com", port="5432", database="bitnami_openerp", user="bn_openerp", password="a865e112")
src_cr = src_db.cursor()

def execute_old_database_query(query, *params):
	try:
		# Query to retrieve source model data
		if params is None:
			src_cr.execute(query)
		else:
			src_cr.execute(query,params)
	except psycopg2.Error as e:
		print e.pgerror

def match_account_period(env, code, name, date_start, date_stop):
	period = env['account.period'].search([('code','=',code),('name','=',name),('date_start','=',date_start),('date_stop','=',date_stop),])
	return period


def match_account_journal(env,type,code):
	# mapping OpenERP 7 journal code to Odoo 8 
	JOURNAL_CODE_OERP2ODOO = {
		'ACOMP': 'ECNJ',
		'Vario': 'MISC',
		'OPEJ': 'OPEJ',
		'BAN1': 'BNK1',
		'BAN2': 'BNK2',
		'STJ': 'STJ',
		'AVENT': 'SCNJ',
		'COMPR': 'EXJ',
		'VEN': 'SAJ'
 	}

	journal = env['account.journal'].search([('type','=',type),('code','=',JOURNAL_CODE_OERP2ODOO[code])])
	return journal

def match_account_fiscal_position(env,name):
	journal = env['account.fiscal.position'].search([('name','=',name)])
	return journal

def match_account_tax(env, type_tax_use, name):
	# mapping OpenERP 7 tax names to Odoo 8
	SALE_TAX_NAME_OERP2ODOO = {
		'IVA 21%': 'IVA 21% (Bienes)',
		'IVA 10%': 'IVA 10% (Bienes)',
		'IVA 4%': 'IVA 4% (Bienes)',
		'IVA 0% Exportaciones': 'IVA 0% Exportaciones',
		'IVA 0% Intracomunitario': 'IVA 0% Entregas Intracomunitarias exentas'
	}
	PURCHASE_TAX_NAME_OERP2ODOO = {
		'Retenciones IRPF 15%': 'Retenciones IRPF 15%',
		'21% IVA Soportado (operaciones corrientes)': '21% IVA soportado (bienes corrientes)',
		'21% IVA Soportado (operaciones corrientes) (Copia)': '21% IVA soportado (bienes corrientes)',
		'10% IVA Soportado (operaciones corrientes)': '10% IVA soportado (bienes corrientes)',
		'4% IVA Soportado (operaciones corrientes)': '4% IVA soportado (bienes corrientes)',
		'IVA 0% Importaciones bienes corrientes': 'IVA Soportado exento (operaciones corrientes)',
		'IVA Soportado exento (operaciones corrientes)': 'IVA Soportado exento (operaciones corrientes)',
		'IVA 20': '21% IVA soportado (bienes corrientes)',
		'IVA 19%': '21% IVA soportado (bienes corrientes)'
	}
	
	if type_tax_use is None or name is None:
		tax = None
		print "************"
		print " TAX = NONE "
		print "************"
		
	else:
		if type_tax_use == 'sale':
			tax = env['account.tax'].search([('type_tax_use','=',type_tax_use),('name','=',SALE_TAX_NAME_OERP2ODOO[name])])
		else:
			tax = env['account.tax'].search([('type_tax_use','=',type_tax_use),('name','=',PURCHASE_TAX_NAME_OERP2ODOO[name])])

	if not tax:
		print "**********************************"
		print "   TAX DOES NOT EXIST IN ODOO 8   "
		print "**********************************"

	return tax
