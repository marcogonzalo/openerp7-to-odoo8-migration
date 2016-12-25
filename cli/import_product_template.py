# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

import psycopg2

class ImportProductTemplate(Command):
    """Import product templates from source DB"""

    def process_item(self, model, data):
        
        if not data:
            return

        # Model structure
        model.create({
            'categ_id': data['categ_id'],
            'company_id': data['company_id'],
            'description': data['description'],
            'list_price': data['list_price'],
            'name': data['name'],
            'sale_ok': data['sale_ok'],
            'state': data['state'],
            'type': data['type'],
            'standard_price': data['standard_price'],
            'brand': data['brand'],
            'subcategory_txt': data['subcategory_txt']
        })

    def run(self, cmdargs):
        print "Deprecated import process. ImportProductProduct does whole work importing each product.product item and its product.template "
        """
        # Connection to the source database
        src_db = psycopg2.connect(
            host="localhost", port="5433",
            database="bitnami_openerp", user="bn_openerp", password="bffbcc4a")

        src_cr = src_db.cursor()
        try:
            # Query to retrieve source model data
            src_cr.execute("" "
                SELECT pt.id, pt.categ_id, pt.company_id, pt.description, pt.list_price, pt.name, pt.sale_ok, pt.standard_price, 
                        pt.state, pt.type, 
                        pp.x_coste, pp.x_marca, pp.x_subcategoria,
                        pc.name, pc.type
                    FROM product_template pt
                        LEFT JOIN product_product pp
                        ON pp.product_tmpl_id = pt.id
                        LEFT JOIN product_category pc
                        on pc.id = pt.categ_id
                    ORDER BY id;
            "" ")
        except psycopg2.Error as e:
            print e.pgerror
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            product_template = env['product.template']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(product_template, c_data)
                    break

                print r
                
                if id_ptr != r[0]:
                    self.process_item(product_template, c_data)
                    id_ptr = r[0]

                    company_id = 1

                    # If category is None or 'All products' in OpenERP 7 can't be searched  
                    if r[2] is None or r[2] == 1:
                        category_id = 1 # -> 'All' in Odoo 8
                    else:
                        category = env['product.category'].search([('name','=',r[13]),('type','=',r[14])])
                        category_id = category.id
                        print category.id,category.id

                    c_data = {
                        'id': r[0],
                        'categ_id': category_id,
                        'company_id': company_id,
                        'description': r[3],
                        'list_price': r[4],
                        'name': r[5],
                        'sale_ok': r[6],
                        'state': r[8],
                        'type': r[9],
                        'standard_price': r[10],
                        'brand': r[11],
                        'subcategory_txt': r[12]
                    }

                    # Hack: type
                    # Change 'product' type to 'consu' for Odoo 8 compatibility issues 
                    if c_data['type'] == 'product':
                        c_data['type'] = 'consu'

                    # Hack: standard_price 
                    # 1) x_coste had the value for standard_price
                    # 2) Drupal use to send prices like integers multiplying by 100
                    if c_data['standard_price'] is not None and c_data['standard_price'].is_integer():
                        c_data['standard_price'] = c_data['standard_price']/100.00
                
        cr.commit()
        cr.close()
        """