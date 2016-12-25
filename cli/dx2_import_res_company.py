# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportResCompany(Command):
    """Import main company from source DB"""

    def run(self, cmdargs):
        print "Importing main company"
        execute_old_database_query("""
            SELECT c.id, c.company_registry, c.name, c.custom_footer, c.partner_id, 
                    c.rml_footer, c.rml_header, c.rml_header1, c.rml_header2, c.rml_header3
                FROM res_company c
                WHERE c.id = 1
                ORDER BY id;
        """)
        
        # Connect to de new database and instanciate db cursor
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            res_company = env['res.company']
            
            r = src_cr.fetchone()
            print r

            # Get element by id
            company = res_company.browse(r[0])
            
            # Rewrite existing element
            company.write({
                'company_registry': r[1],
                'name': r[2],
                'custom_footer': r[3],
                'partner_id': 1,
                'rml_footer': r[5],
                'rml_header': r[6],
                'rml_header1': r[7],
                'rml_header2': r[8],
                'rml_header3': r[9],
            })
            
        cr.commit()
        cr.close()