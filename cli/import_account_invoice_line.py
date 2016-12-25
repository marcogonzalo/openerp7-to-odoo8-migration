# -*- coding: utf-8 -*-
from datetime import datetime

import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportAccountInvoiceLine(Command):
    """Import account invoice lines from source DB"""

    def process_account_invoice_line(self, model, data):
        if not data:
            return

        m = {
            'account_id': data['account_id'],
            'create_date': data['create_date'],
            'company_id': data['company_id'],
            'discount': data['discount'],
            'invoice_id': data['invoice_id'],
            'name': data['name'],
            'partner_id': data['partner_id'],
            'product_id': data['product_id'],
            'quantity': data['quantity'],
            'price_unit': data['price_unit'],
            'price_subtotal': data['price_subtotal'],
            'supplier_name': data['supplier_name'],
            'supplier_ref': data['supplier_ref'],
            'item_lot_number': data['item_lot_number'],
            'item_expiration': data['item_expiration'],
            'item_delivery_note': data['item_delivery_note'],
        }

        if not data['invoice_line_tax_id'] is None:
            m['invoice_line_tax_id'] = [(4,data['invoice_line_tax_id'])] # http://stackoverflow.com/questions/31853402/filling-many2many-field-odoo-8
        
        # Model structure
        model.create(m)

    def refresh_invoices_and_recompute_taxes(self, model,invoice_ids):
        for i in invoice_ids:
            print "Updating invoice", i
            invoice = model.browse(i)
            print invoice.origin, invoice.id, invoice.state, invoice.type
            print "- Computing taxes"
            invoice.button_compute(set_total=True)
            invoice.action_date_assign()
            print "- Creating account move"
            invoice.action_move_create()
            print invoice.number, invoice.internal_number, invoice.move_id.name
            if None in [invoice.number,invoice.move_id,invoice.move_id.name]:
                print '********************************'
                print invoice.number,invoice.move_id,invoice.move_id.name
                print '********************************'
            print "- Assigning number"
            invoice.action_number()


    def run(self, cmdargs):
        print "Deprecated import process. ImportSaleOrder does whole work importing each sale.order and its sale.order.line"
        """
        print "Importing account invoice lines"
        execute_old_database_query("" "
            SELECT il.id, il.account_id, il.create_date, il.company_id, il.discount, il.invoice_id, il.name, il.partner_id, il.price_unit, 
                    il.price_subtotal, il.product_id, il.quantity, il.x_prov, il.x_ref_prov, il.x_lote, il.x_caducidad, il.x_albaran,
                    i.internal_number, i.name, i.origin, i.reference, i.type, i.x_drupal_order, i.date_invoice,
                    rp.email, rp.name, rp.type, rp.vat, rp.street,
                    pp.default_code, pp.name_template, pp.x_subcategoria, pp.x_marca,
                    at.type_tax_use, at.name
                FROM account_invoice_line il
                    LEFT JOIN account_invoice i
                        ON i.id = il.invoice_id
                    LEFT JOIN res_partner rp
                        ON rp.id = il.partner_id
                    LEFT JOIN product_product pp
                        ON pp.id = il.product_id
                    LEFT JOIN account_invoice_line_tax ailt
                        ON ailt.invoice_line_id = il.id
                    LEFT JOIN account_tax at
                        ON at.id = ailt.tax_id
                ORDER BY il.invoice_id ASC, il.id ASC;
        "" ")
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        invoice_ids = []
        inv_id = 0

        contador = 0
        success = 0
        no_account_invoice = 0
        no_invoice = 0

        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            account_invoice_line = env['account.invoice.line']
            
            id_ptr = None
            c_data = {}

            company_id = 1
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_account_invoice_line(account_invoice_line, c_data)
                    break

                contador += 1
                print r

                print r[17],r[18],r[19],r[20],r[21]

                if not (r[17] is None and r[18] is None and r[19] is None and r[20] is None):
                    account_invoice = env['account.invoice'].search([('internal_number','=',r[17]),('name','=',r[18]),('origin','=',r[19]),('reference','=',r[20]),('type','=',r[21]),('drupal_order_name','=',r[22]),('date_invoice','=',r[23])])
                    print "normal"
                else:
                    print "parner"
                    if r[27] is not None and r[28] is not None:
                        partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('type','=',r[26]),('vat','=',r[27]),('street','=',r[28])])
                    elif r[27] is not None:
                        partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('type','=',r[26]),('vat','=',r[27])])
                    elif r[28] is not None:
                        partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('type','=',r[26]),('street','=',r[28])])
                    else:
                        partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('type','=',r[26])])

                    # Take one when partners are duplicated
                    partner_id = partner.id if len(list(partner)) <= 1 else partner[0].id
                    account_invoice = env['account.invoice'].search([('internal_number','=',r[17]),('name','=',r[18]),('origin','=',r[19]),('reference','=',r[20]),('type','=',r[21]),('drupal_order_name','=',r[22]),('date_invoice','=',r[23]),('partner_id','=',partner_id)])
                    
                    if not account_invoice: # If there is not an account_invoice for this partner, continue with the next row
                        print "^ NO INVOICE FOR THIS LINE ^"
                        no_account_invoice += 1
                        continue 

                product = env['product.product'].search([('default_code','=',r[29]),('name_template','=',r[30]),('subcategory_txt','=',r[31]),('brand','=',r[32])])
                
                # Take one when invoices are duplicated
                invoice = account_invoice if len(list(account_invoice)) <= 1 else account_invoice[0]
                # Take one when products are duplicated
                product_id = product.id if len(list(product)) <= 1 else product[0].id
                if not invoice:
                    no_invoice += 1
                    continue
                else:
                    if inv_id != invoice.id:
                        inv_id = invoice.id
                        invoice_ids.append(inv_id)

                print invoice

                print r[33],r[34]
                tax = match_account_tax(env, r[33], r[34])
                tax_id = tax.id if tax is not None and tax else None

                if id_ptr != r[0]:
                    id_ptr = r[0]
                    c_data = {
                        'id': r[0],
                        'account_id': invoice.account_id.id,
                        'create_date': r[2],
                        'company_id': r[3],
                        'discount': r[4],
                        'invoice_id': invoice.id,
                        'name': r[6],
                        'partner_id': invoice.partner_id.id,
                        'price_unit': r[8],
                        'price_subtotal': r[9],
                        'product_id': product_id,
                        'quantity': r[11],
                        'supplier_name': r[12],
                        'supplier_ref': r[13],
                        'item_lot_number': r[14],
                        'item_expiration': r[15],
                        'item_delivery_note': r[16],
                        'invoice_line_tax_id': tax_id
                    }

                    success += 1
                    self.process_account_invoice_line(account_invoice_line, c_data)

            self.refresh_invoices_and_recompute_taxes(env['account.invoice'], invoice_ids)
        print contador, success, no_account_invoice, no_invoice
#        cr.commit()
#        cr.close()
        """