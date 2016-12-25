# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportSaleOrderLine(Command):
    """Import sale order lines from source DB"""

    def process_item(self, model, data):
        if not data:
            return

        # Model structure
        m = {
            'create_date': data['create_date'],
            'company_id': data['company_id'],
            'discount': data['discount'],
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
        }
        
        if not data['tax_id'] is None:
            m['tax_id'] = [(4,data['tax_id'])] # http://stackoverflow.com/questions/31853402/filling-many2many-field-odoo-8
       
        model.create(m)


    def run(self, cmdargs, invoice = None, old_invoice_id = 0):
        print "Deprecated import process. ImportSaleOrder does whole work importing each sale.order and its sale.order.line"
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
                ORDER BY sol.id;
        """)
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            sale_order_line = env['sale.order.line']
            
            id_ptr = None
            c_data = {}

            company_id = 1
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(sale_order_line, c_data)
                    break

                print r

                sale_order = None
                if r[18] is not None:
                    sale_order = env['sale.order'].search([('name','=',r[17]),('drupal_order_name','=',r[18])])
                    print "aqui"
                else:
                    sale_order = env['sale.order'].search([('name','=',r[17])])
                    print "aca"

                print sale_order
                print sale_order.name

                product = env['product.product'].search([('default_code','=',r[20]),('name_template','=',r[21]),('subcategory_txt','=',r[22]),('brand','=',r[23])])

                # Take one when partners are duplicated
                product_id = product.id if len(list(product)) <= 1 else product[0].id

                print r[24],r[25]
                tax = match_account_tax(env, r[24], r[25])
                tax_id = tax.id if tax is not None and tax else None
                
                if id_ptr != r[0] and sale_order:
                    self.process_item(sale_order_line, c_data)
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
                        'tax_id': tax_id,
                        'type': r[13],
                        'supplier_name': r[14],
                        'supplier_ref': r[15]
                    }
                
        cr.commit()
        cr.close()