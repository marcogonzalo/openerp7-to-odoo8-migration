# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportAccountFiscalyear(Command):
    """Import fiscalyear and periods from source DB"""

    def process_fiscalyear(self, model, data):
        if not data:
            return
        # Model structure
        model.create({
            'code': data['code'], 
            'company_id': data['company_id'], 
            'create_date': data['create_date'], 
            'date_start': data['date_start'], 
            'date_stop': data['date_stop'], 
            'name': data['name']
        })

    def run(self, cmdargs):
        print "Importing account fiscal years"
        execute_old_database_query("""
            SELECT fy.id, fy.code, fy.company_id, fy.create_date, fy.date_start, fy.date_stop, fy.name
            FROM account_fiscalyear fy 
            WHERE fy.company_id = 1 
            ORDER BY fy.id;
        """)
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            account_fiscalyear = env['account.fiscalyear']

            id_fy_ptr = None
            fy_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_fiscalyear(account_fiscalyear, fy_data)
                    break
                
                print r
                                
                company_id = 1
                # If fiscalyear.id is different to last id
                if id_fy_ptr != r[0]:
                    self.process_fiscalyear(account_fiscalyear, fy_data)
                    id_fy_ptr = r[0]
                    fy_data = {
                        'id': r[0], 
                        'code': r[1], 
                        'company_id': company_id, 
                        'create_date': r[3], 
                        'date_start': "{0}-01-01".format(r[1]), 
                        'date_stop': "{0}-12-31".format(r[1]), 
                        'name': r[6]
                    }
                
        cr.commit()
        cr.close()