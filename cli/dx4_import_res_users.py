# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportResUsers(Command):
    """Import users from source DB"""
    def process_item(self, model, data):
        
        if not data:
            return
        # Model structure
        model.create({
            'active': data['active'],
            'company_id': data['company_id'],
            'create_date': data['create_date'],
            'login': data['login'],
            'partner_id': data['partner_id'],
            'password': data['password']
        })

    def run(self, cmdargs):
        print "Importing users"
        execute_old_database_query("""
            SELECT u.id, u.active, u.company_id, u.create_date, u.login, u.partner_id, u.password,
                    p.id, p.email, p.name, p.type, p.vat, p.street
                FROM res_users u
                    LEFT JOIN res_partner p
                    ON p.id = u.partner_id
                WHERE u.id > 3 
                ORDER BY u.id;
        """)

        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            res_users = env['res.users']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(res_users, c_data)
                    break

                print r

                company_id = 1
                if r[11] is not None and r[12] is not None:
                    partner = env['res.partner'].search([('email','=',r[8]),('name','=',r[9]),('type','=',r[10]),('vat','=',r[11]),('street','=',r[12])])
                elif r[11] is not None:
                    partner = env['res.partner'].search([('email','=',r[8]),('name','=',r[9]),('type','=',r[10]),('vat','=',r[11])])
                elif r[12] is not None:
                    partner = env['res.partner'].search([('email','=',r[8]),('name','=',r[9]),('type','=',r[10]),('street','=',r[12])])
                else:
                    partner = env['res.partner'].search([('email','=',r[8]),('name','=',r[9]),('type','=',r[10])])

                # Take one when partners are duplicated
                partner_id = partner.id if len(list(partner)) <= 1 else partner[0].id
                
                if id_ptr != r[0]:
                    self.process_item(res_users, c_data)
                    id_ptr = r[0]
                    c_data = {
                        'id': r[0],
                        'active': r[1],
                        'company_id': company_id,
                        'create_date': r[3],
                        'login': r[4],
                        'partner_id': partner_id,
                        'password': r[6]
                    }
                
        cr.commit()
        cr.close()