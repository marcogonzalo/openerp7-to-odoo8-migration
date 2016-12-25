# -*- coding: utf-8 -*-
from datetime import datetime

import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportAccountInvoice(Command):
    """Import account invoices from source DB"""

    def process_account_invoice(self, model, data):
        if not data:
            return

        # Model structure
        m = model.create({
            'account_id': data['account_id'],
#            'amount_tax': data['amount_tax'],
#            'amount_total': data['amount_total'],
#            'amount_untaxed': data['amount_untaxed'],
#            'check_total': data['check_total'],
            'company_id': data['company_id'],
            'currency_id': data['currency_id'],
            'date_due': data['date_due'],
            'date_invoice': data['date_invoice'],
            'fiscal_position': data['fiscal_position'],
            'internal_number': data['internal_number'],
#            'move_name': data['move_name'],
            'name': data['name'],
            'origin': data['origin'],
            'partner_id': data['partner_id'],
            'period_id': data['period_id'],
#            'reconciled': data['reconciled'],
            'reference': data['reference'],
#            'residual': data['residual'],
            'state': data['state'],
            'type': data['type'],
            'ship_addr_city': data['ship_addr_city'],
            'ship_addr_name': data['ship_addr_name'],
            'client_notes': data['client_notes'],
            'ship_addr_state': data['ship_addr_state'],
            'ship_addr_street': data['ship_addr_street'],
            'ship_addr_phone': data['ship_addr_phone'],
            'ship_addr_zip': data['ship_addr_zip'],
            'drupal_order_name': data['drupal_order_name'],
            'payment_method': data['payment_method'],
            'drupal_total': data['drupal_total']
        })
        return m

    def process_account_invoice_line(self, model, data):
        if not data:
            return

        # Model structure
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
        
        model.create(m)

    def refresh_invoices_and_recompute_taxes(self, invoice):
        #for i in invoice_ids:
        print "Updating invoice", invoice.id
        #invoice = model.browse(i)
        print invoice.origin, invoice.id, invoice.state, invoice.type
        print "- Computing taxes"
        invoice.button_compute(set_total=True)
        invoice.action_date_assign()
        print "- Creating account move"
        if (invoice.state != 'draft' and invoice.state != 'cancel') or (invoice.state == 'cancel' and invoice.internal_number is not None): 
            invoice.action_move_create()
            print invoice.number, invoice.internal_number, invoice.move_id.name
            if None in [invoice.number,invoice.move_id,invoice.move_id.name]:
                print '********************************'
                print invoice.number,invoice.move_id,invoice.move_id.name
                print '********************************'
            print "- Assigning number"
            invoice.action_number()

    def run_invoice_line_migration(self, r, cr, invoice_ids_match):
        print "Importing account invoice lines"
        for invoice_id, i_id in invoice_ids_match.iteritems():
            execute_old_database_query("""
                SELECT il.id, il.account_id, il.create_date, il.company_id, il.discount, il.invoice_id, il.name, 
                        il.partner_id, il.price_unit, il.price_subtotal, il.product_id, il.quantity, il.x_prov, 
                        il.x_ref_prov, il.x_lote, il.x_caducidad, il.x_albaran,
                        rp.email, rp.name, rp.type, rp.vat, rp.street,
                        pp.default_code, pp.name_template, pp.x_subcategoria, pp.x_marca,
                        at.type_tax_use, at.name
                    FROM account_invoice_line il
                        LEFT JOIN res_partner rp
                            ON rp.id = il.partner_id
                        LEFT JOIN product_product pp
                            ON pp.id = il.product_id
                        LEFT JOIN account_invoice_line_tax ailt
                            ON ailt.invoice_line_id = il.id
                        LEFT JOIN account_tax at
                            ON at.id = ailt.tax_id
                    WHERE il.invoice_id = %s
                    ORDER BY il.id ASC;
            """,(invoice_id,))

            with api.Environment.manage():
                env = api.Environment(cr, 1, {})
                # Define target model 
                account_invoice= env['account.invoice']
                account_invoice_line = env['account.invoice.line']
                
                id_ptr = None
                c_data = {}

                company_id = 1
                while True:
                    r = src_cr.fetchone()
                    if not r:
                        self.process_account_invoice_line(account_invoice_line, c_data)
                        break

                    print r

                    invoice = account_invoice.browse(i_id)

                    product = env['product.product'].search([('default_code','=',r[22]),('name_template','=',r[23]),('subcategory_txt','=',r[24]),('brand','=',r[25])])
                    
                    # Take one when invoices are duplicated
                    # invoice = account_invoice if len(list(account_invoice)) <= 1 else account_invoice[0]
                    # Take one when products are duplicated
                    product_id = product.id if len(list(product)) <= 1 else product[0].id
                    if not invoice:
                        continue

                    print invoice

                    print r[26],r[27]
                    tax = match_account_tax(env, r[26], r[27])
                    tax_id = tax.id if tax is not None and tax else None

                    if id_ptr != r[0]:
                        id_ptr = r[0]
                        self.process_account_invoice_line(account_invoice_line, c_data)
                        c_data = {
                            'id': r[0],
                            'account_id': invoice.account_id.id,
                            'create_date': r[2],
                            'company_id': company_id,
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


                self.refresh_invoices_and_recompute_taxes(invoice)
        cr.commit()

    def run_invoice_migration(self, r, cr):
        print "Importing account invoices"
        execute_old_database_query("""
            SELECT i.id, i.account_id, i.amount_tax, i.amount_total, i.amount_untaxed, i.check_total, i.company_id, i.currency_id, i.date_due, 
                    i.date_invoice, i.fiscal_position, i.internal_number, i.journal_id, i.move_name, i.name, i.origin, i.partner_id, i.period_id, 
                    i.reconciled, i.reference, i.residual, i.sent, i.state, i.type, i.x_dir_city, i.x_dir_name, i.x_dir_observations, 
                    i.x_dir_state, i.x_dir_street, i.x_dir_telephone, i.x_dir_zip, i.x_drupal_order, i.x_pago, i.x_total,
                    rp.id, rp.email, rp.name, rp.type, rp.vat, rp.street,
                    rc.id, rc.name,
                    aa.id, aa.code, aa.name,
                    ap.id, ap.code, ap.name, ap.date_start, ap.date_stop,
                    aj.type, aj.code,
                    fp.name
                FROM account_invoice i
                    LEFT JOIN res_partner rp
                        ON rp.id = i.partner_id
                    LEFT JOIN res_currency rc
                        ON rc.id = i.currency_id
                    LEFT JOIN account_account aa
                        ON aa.id = i.account_id
                    LEFT JOIN account_period ap
                        ON ap.id = i.partner_id
                    LEFT JOIN account_journal aj
                        ON aj.id = i.journal_id
                    LEFT JOIN account_fiscal_position fp
                        ON fp.id = i.fiscal_position
                ORDER BY i.id;
        """)
        
        
        oerp_invid_2_odoo_invid = {}
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            account_invoice = env['account.invoice']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_account_invoice(account_invoice, c_data)
                    break

                print r

                account = env['account.account'].search([('code','=',r[43]),('name','=',r[44]),])
                currency = env['res.currency'].search([('name','=',r[41]),])

                period = match_account_period(env,code=r[46],name=r[47],date_start=r[48],date_stop=r[49])
                journal = match_account_journal(env,type=r[50],code=r[51])
                fiscal_position = match_account_fiscal_position(env,name=r[52])

                company_id = 1
                if r[38] is not None and r[39] is not None:
                    partner = env['res.partner'].search([('email','=',r[35]),('name','=',r[36]),('type','=',r[37]),('vat','=',r[38]),('street','=',r[39])])
                elif r[38] is not None:
                    partner = env['res.partner'].search([('email','=',r[35]),('name','=',r[36]),('type','=',r[37]),('vat','=',r[38])])
                elif r[39] is not None:
                    partner = env['res.partner'].search([('email','=',r[35]),('name','=',r[36]),('type','=',r[37]),('street','=',r[39])])
                else:
                    partner = env['res.partner'].search([('email','=',r[35]),('name','=',r[36]),('type','=',r[37])])

                # Take one when partners are duplicated
                partner_id = partner.id if len(list(partner)) <= 1 else partner[0].id
                fiscal_position_id = fiscal_position.id if fiscal_position else None

                if id_ptr != r[0]:
                    id_ptr = r[0]
                    c_data = {
                        'id': r[0],
                        'account_id': account.id,
                        'amount_tax': r[2],
                        'amount_total': r[3],
                        'amount_untaxed': r[4],
                        'check_total': r[5],
                        'company_id': company_id,
                        'currency_id': currency.id,
                        'date_due': r[8],
                        'date_invoice': r[9],
                        'fiscal_position': fiscal_position_id,
                        'internal_number': r[11],
                        'journal_id': journal.id,
                        'move_name': r[13],
                        'name': r[14],
                        'origin': r[15],
                        'partner_id': partner_id,
                        'partner_invoice_id': partner_id,
                        'partner_shipping_id': partner_id,
                        'period_id': period.id,
                        'reconciled': r[18],
                        'reference': r[19],
                        'residual': r[20],
                        'sent': r[21],
                        'state': r[22],
                        'type': r[23],
                        'ship_addr_city': r[24],
                        'ship_addr_name': r[25],
                        'client_notes': r[26],
                        'ship_addr_state': r[27],
                        'ship_addr_country': '',
                        'ship_addr_street': r[28],
                        'ship_addr_phone': r[29],
                        'ship_addr_zip': r[30],
                        'drupal_order_name': r[31],
                        'payment_method': r[32],
                        'drupal_total': r[33]
                    }
                    m = self.process_account_invoice(account_invoice, c_data)

                    if m is None:
                        continue

                    oerp_invid_2_odoo_invid[r[0]] = m.id

            cr.commit()

            self.run_invoice_line_migration(r, cr, oerp_invid_2_odoo_invid)

    def run(self, cmdargs):
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()

        self.run_invoice_migration(r, cr)

        cr.close()
