# -*- coding: utf-8 -*-
import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportResPartnerSuperadmin(Command):
    """Import superadmin from source DB"""

    def run(self, cmdargs):
        print "Importing superadmin"
        execute_old_database_query("""
            SELECT id, active, company_id, city, country_id, create_date, create_uid, customer, date, display_name, email, 
                    employee, fax, is_company, lang, mobile, parent_id, phone, state_id, street, street2, supplier, type, 
                    tz, use_parent_address, user_id, vat, website, zip, name
                FROM res_partner
                WHERE id = 1;
        """)
        
        # Connect to de new databas and instanciate db cursor
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            res_partner = env['res.partner']
            
            r = src_cr.fetchone()
            print r

            company_id = 1
            country = env['res.country'].search([('name','like',r[25])])

            # Hack: lang
            # Repair custom languages duplicating es_ES
            if r[14] == 254:
                r[14] = 69

            # Get element by id
            partner = res_partner.browse(r[0])

            partner.write({
                'active': r[1],
                'company_id': company_id,
                'city': r[3],
                'country_id': country.id,
                'create_date': r[5],
                'create_uid': r[6],
                'customer': r[7],
                'date': r[8],
                'display_name': r[9],
                'email': r[10],
                'employee': r[11],
                'fax': r[12],
                'is_company': r[13],
                'lang': r[14],
                'mobile': r[15],
                'parent_id': r[16],
                'phone': r[17],
                'street': r[19],
                'street2': r[20],
                'supplier': r[21],
                'type': r[22],
                'tz': r[23],
                'use_parent_address': r[24],
                'vat': r[26],
                'website': r[27],
                'zip': r[28],
                'name': r[29]
            })
            
        cr.commit()
        cr.close()