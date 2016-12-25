# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportAccountPeriod(Command):
    """Import period and periods from source DB"""

    def process_period(self, model, data):
        if not data:
            return
        # Model structure
        model.create({
            'code': data['code'], 
            'company_id': data['company_id'], 
            'create_date': data['create_date'], 
            'date_start': data['date_start'], 
            'date_stop': data['date_stop'], 
            'fiscalyear_id': data['fiscalyear_id'], 
            'name': data['name'], 
            'special': data['special'], 
            'state': data['state']
        })

    def run(self, cmdargs):
        print "Importing account periods"
        execute_old_database_query("""
            SELECT pd.id, pd.code, pd.company_id, pd.create_date, pd.date_start, pd.date_stop, pd.name, pd.special, pd.state,
                    fy.id, fy.name, fy.code
                FROM account_period pd
                    LEFT JOIN account_fiscalyear fy
                    ON fy.id = pd.fiscalyear_id
                WHERE pd.company_id = 1
                ORDER BY pd.id;
        """)
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            account_period = env['account.period']

            id_pd_ptr = None
            pd_data = {}
            while True:
                r = src_cr.fetchone()                
                if not r:
                    self.process_period(account_period, pd_data)
                    break
                
                print r
                
                company_id = 1
                fiscalyear = env['account.fiscalyear'].search([('name','=',r[10]),('code','=',r[11]),('company_id','=',company_id)])

                # If period.id is different to last id
                if id_pd_ptr != r[0]:
                    self.process_period(account_period, pd_data)
                    id_pd_ptr = r[0]
                    pd_data = {
                        'code': r[1], 
                        'company_id': company_id, 
                        'create_date': r[3], 
                        'date_start': r[4], 
                        'date_stop': r[5],
                        'fiscalyear_id': fiscalyear.id, 
                        'name': r[6], 
                        'special': r[7], 
                        'state': r[8]
                    }
                
        cr.commit()
        cr.close()