    # -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportProductProduct(Command):
    """Import product products and their associated templates from source DB"""

    def process_item(self, model, data):        
        if not data:
            return

        # Model structure
        model.create({
            'company_id': data['company_id'],
            'active': data['active'],
            'create_date': data['create_date'],
            'default_code': data['default_code'],
            'brand': data['brand'],
            'on_offer': data['on_offer'],
            'subcategory_txt': data['subcategory_txt'],
            'name': data['name'],
            'categ_id': data['categ_id'],
            'description': data['description'],
            'list_price': data['list_price'],
            'name': data['name'],
            'sale_ok': True,
            'state': data['state'],
            'type': 'consu',
            'standard_price': data['standard_price']
        })

    def run(self, cmdargs):
        print "Importing products"
        execute_old_database_query("""
            SELECT pp.id, pp.active, pp.create_date, pp.default_code, pp.product_tmpl_id, pp.x_coste, 
                    pp.x_marca, pp.x_oferta, pp.x_subcategoria,
                    pt.categ_id, pt.description, pt.list_price, pt.name, pt.sale_ok, pt.state, pt.type, pt.standard_price,
                    pc.name, pc.type
                FROM product_product pp
                    LEFT JOIN product_template pt
                    ON pt.id = pp.product_tmpl_id
                    LEFT JOIN product_category pc
                    ON pc.id = pt.categ_id
                ORDER BY pp.id;
        """)
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            product_product = env['product.product']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(product_product, c_data)
                    break

                print r
                
                if id_ptr != r[0]:
                    self.process_item(product_product, c_data)
                    id_ptr = r[0]

                    company_id = 1

                    # If category is None or 'All products' in OpenERP 7 can't be searched  
                    if r[9] is None or r[9] == 1:
                        category_id = 1 # -> 'All' in Odoo 8
                    else:
                        category = env['product.category'].search([('name','=',r[17]),('type','=',r[18])])
                        category_id = category.id

                    c_data = {
                        'id': r[0],
                        'company_id': company_id,
                        'active': r[1],
                        'create_date': r[2],
                        'default_code': r[3],
                        'brand': r[6],
                        'on_offer': r[7],
                        'subcategory_txt': r[8],

                        'categ_id': category_id,
                        'description': r[10],
                        'list_price': r[11],
                        'name': r[12],
                        'sale_ok': True,
                        'state': r[14],
                        'type': 'consu',
                        'standard_price': r[16]
                    }
                    
                    # Hack: standard_price 
                    # 1) x_coste had the value for standard_price
                    # 2) Drupal use to send prices like integers multiplying by 100
                    if c_data['standard_price'] is not None and c_data['standard_price'].is_integer():
                        c_data['standard_price'] = c_data['standard_price']/100.00

        cr.commit()
        cr.close()