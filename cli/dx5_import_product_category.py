# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportProductCategory(Command):
    """Import categories from source DB"""

    def process_item(self, model, data):
        if not data:
            return
        # Model structure
        model.create({
            'id': data['id'],
            'parent_id': None,
            'type': data['type'],
            'name': data['name']
        })

        # !!!
        # MAS COSAS QUE HACER AQUI
        # !!!

    def run(self, cmdargs):
        print "Importing product categories"
        execute_old_database_query("""
            SELECT c.id, c.parent_id, c.name, c.type 
                FROM product_category c
                WHERE c.id > 2
                ORDER BY c.id;
        """)

        """In case of need to include translations, include the following LEFT JOIN sentence
        
        
            LEFT JOIN ir_translation t
                ON t.res_id = c.id
                AND t."name" = 'product.category,name'
        """
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
                
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            product_category = env['product.category']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(product_category, c_data)
                    break
                
                print r
                                
                if id_ptr != r[0]:
                    self.process_item(product_category, c_data)
                    id_ptr = r[0]
                    c_data = {
                        'id': r[0],
                        'parent_id': r[1],
                        'name': r[2],
                        'type': r[3]
                    }

                """
                # In case of need to include translations
                        ,
                        'l18n': [{
                            'lang': r[4],
                            'value': r[5]
                        }]
                    }
                else:
                    c_data['l18n'].append({
                            'lang': r[4],
                            'value': r[5]
                    })
                """
                
        cr.commit()
        cr.close()