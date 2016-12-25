# -*- coding: utf-8 -*-
from datetime import datetime

import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportSaleOrder(Command):
    """Import sale orders from source DB"""

    def process_sale_order(self, model, data):
        if not data:
            return

        # Model structure
        m = model.create({
            'company_id': data['company_id'],
            'create_date': data['create_date'],
            'date_confirm': data['date_confirm'],
            'date_order': data['date_order'],
            'name': data['name'],
            'note': data['note'],
            'origin': data['origin'],
            'partner_id': data['partner_id'],
            'partner_invoice_id': data['partner_invoice_id'],
            'partner_shipping_id': data['partner_shipping_id'],
            'shop_id': data['shop_id'],
            'shipped': data['shipped'],
            'state': data['state'],
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
        
    def process_sale_order_line(self, model, data):
        if not data:
            return

        # Model structure
        model.create({
            'create_date': data['create_date'],
            'company_id': data['company_id'],
            'invoiced': data['invoiced'],
            'name': data['name'],
            'order_id': data['order_id'],
            'product_id': data['product_id'],
            'product_uom': data['product_uom'],
            'product_uom_qty': data['product_uom_qty'],
            'product_uos': data['product_uos'],
            'product_uos_qty': data['product_uos_qty'],
            'price_unit': data['price_unit'],
            'type': data['type'],
            'supplier_name': data['supplier_name'],
            'supplier_ref': data['supplier_ref']
        })

    def run_sale_order_line_migration(self, r, cr, sale_order_ids_match):
        print "Importing sale order lines"

        for sale_order_id, so_id in sale_order_ids_match.iteritems():
            execute_old_database_query("""
                SELECT sol.id, sol.create_date, sol.company_id, sol.discount, sol.invoiced, sol.name, sol.order_id, sol.product_id, 
                        sol.product_uom, sol.product_uom_qty, sol.product_uos, sol.product_uos_qty, sol.price_unit, sol.type, 
                        sol.x_prov, sol.x_ref_prov, 
                        so.id, so.name, so.x_drupal_order, 
                        pp.id, pp.default_code, pp.name_template, pp.x_subcategoria, pp.x_marca,
                        at.type_tax_use, at.name
                    FROM sale_order_line sol
                        LEFT JOIN sale_order so
                        ON so.id = sol.order_id
                        LEFT JOIN product_product pp
                        ON pp.id = sol.product_id
                        LEFT JOIN sale_order_tax sot
                            ON sot.order_line_id = sol.id
                        LEFT JOIN account_tax at
                            ON at.id = sot.tax_id
                    WHERE sol.order_id = %s
                    ORDER BY sol.id;
            """,(sale_order_id,))
            
            with api.Environment.manage():
                env = api.Environment(cr, 1, {})
                # Define target model 
                sale_order = env['sale.order']
                sale_order_line = env['sale.order.line']
                
                id_ptr = None
                c_data = {}

                company_id = 1
                while True:
                    r = src_cr.fetchone()
                    if not r:
                        self.process_sale_order_line(sale_order_line, c_data)
                        break

                    print r

                    sale_order = sale_order.browse(so_id)
                    if not sale_order:
                        continue

                    product = env['product.product'].search([('default_code','=',r[20]),('name_template','=',r[21]),('subcategory_txt','=',r[22]),('brand','=',r[23])])

                    # Take one when partners are duplicated
                    product_id = product.id if len(list(product)) <= 1 else product[0].id

                    tax = match_account_tax(env, r[24], r[25])
                    tax_id = tax.id if tax is not None and tax else None

                    if id_ptr != r[0]:
                        self.process_sale_order_line(sale_order_line, c_data)
                        id_ptr = r[0]
                        c_data = {
                            'id': r[0],
                            'create_date': r[1],
                            'company_id': company_id,
                            'discount': r[3],
                            'invoiced': r[4],
                            'name': r[5],
                            'order_id': sale_order.id,
                            'product_id': product_id,
                            'product_uom': r[8],
                            'product_uom_qty': r[9],
                            'product_uos': r[10],
                            'product_uos_qty': r[11],
                            'price_unit': r[12],
                            'type': r[13],
                            'supplier_name': r[14],
                            'supplier_ref': r[15]
                        }
                
        cr.commit()


    def run_sale_order_migration(self, r, cr):
        print "Importing sale orders"
        execute_old_database_query("""
            SELECT so.id, so.company_id, so.client_order_ref, so.create_date, so.date_confirm, so.date_order, so.name, so.note, 
                    so.origin, so.partner_id, so.shop_id, so.shipped, so.state, so.x_dir_city, so.x_dir_name, so.x_dir_observations, 
                    so.x_dir_state, so.x_dir_street, so.x_dir_telephone, so.x_dir_zip, so.x_drupal_order, so.x_pago, so.x_total,
                    p.id, p.email, p.name, p.street, p.vat, p.type
                FROM sale_order so
                    LEFT JOIN res_partner p
                        ON p.id = so.partner_id
                WHERE (so.state NOT IN ('draft', 'cancel') OR (so.state = 'draft' AND so.date_order > CAST('2016-09-01' AS DATE))) AND so.id > 0 AND so.id <= 2000
                ORDER BY so.id;
        """)
        
        oerp_saoid_2_odoo_saoid = {}
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            sale_order = env['sale.order']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_sale_order(sale_order, c_data)
                    break

                print r
                
                company_id = 1
                if r[26] is not None and r[27] is not None:
                    partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('street','=',r[26]),('vat','=',r[27]),('type','=',r[28])])
                elif r[27] is not None:
                     partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('vat','=',r[27]),('type','=',r[28])])
                elif r[26] is not None:
                    partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('street','=',r[26]),('type','=',r[28])])
                else:
                    partner = env['res.partner'].search([('email','=',r[24]),('name','=',r[25]),('type','=',r[28])])

                partner_id = partner.id if len(list(partner)) <= 1 else partner[0].id

                if id_ptr != r[0]:
                    id_ptr = r[0]
                    c_data = {
                        'id': r[0],
                        'company_id': company_id,
                        'client_order_ref': r[2],
                        'create_date': r[3],
                        'date_confirm': r[4],
                        'date_order': r[5],
                        'name': r[6],
                        'note': r[7],
                        'origin': r[8],
                        'partner_id': partner_id,
                        'partner_invoice_id': partner_id,
                        'partner_shipping_id': partner_id,
                        'shop_id': None,
                        'shipped': r[11],
                        'state': r[12],
                        'ship_addr_city': r[13],
                        'ship_addr_name': r[14],
                        'client_notes': r[15],
                        'ship_addr_state': r[16],
                        'ship_addr_street': r[17],
                        'ship_addr_phone': r[18],
                        'ship_addr_zip': r[19],
                        'drupal_order_name': r[20],
                        'payment_method': r[21],
                        'drupal_total': r[22]
                    }

                    # Hack: date_order 
                    # Conver date_order fomr date value in OpenERP 7 to datetime value in Odoo 8
                    c_data['date_order'] = datetime.strptime(c_data['date_order']+" 00:00:00", "%Y-%m-%d %H:%M:%S")

                    m = self.process_sale_order(sale_order, c_data)                    
                    
                    if m is None:
                        continue

                    oerp_saoid_2_odoo_saoid[r[0]] = m.id

            cr.commit()

            self.run_sale_order_line_migration(r, cr, oerp_saoid_2_odoo_saoid)

    def run(self, cmdargs):
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        self.run_sale_order_migration(r, cr)
        
        cr.close()
