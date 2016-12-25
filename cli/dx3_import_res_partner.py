import openerp
from openerp import api, modules
from openerp.cli import Command

from dentaltix_conn import *

class ImportResPartner(Command):
    """Import partners from source DB"""

    def process_item(self, model, data):
        if not data:
            return
        # Model structure
        model.create({
            'active': data['active'],
            'company_id': data['company_id'],
            'city': data['city'],
            'country_id': data['country_id'],
            'create_date': data['create_date'],
            'create_uid': None,
            'customer': data['customer'],
            'date': data['date'],
            'display_name': data['display_name'],
            'email': data['email'],
            'employee': data['employee'],
            'fax': data['fax'],
            'is_company': data['is_company'],
            'lang': data['lang'],
            'mobile': data['mobile'],
            'name': data['name'],
            'parent_id': None,
            'phone': data['phone'],
            'state_id': None,
            'street': data['street'],
            'street2': data['street2'],
            'supplier': data['supplier'],
            'type': data['type'],
            'tz': data['tz'],
            'use_parent_address': data['use_parent_address'],
            'user_id': None,
            'vat': data['vat'],
            'website': data['website'],
            'zip': data['zip']
        })

    def run(self, cmdargs):
        print "Importing partners"
        execute_old_database_query("""
            SELECT p1.id, p1.active, p1.company_id, p1.city, p1.country_id, p1.create_date, p1.create_uid, p1.customer, 
                    p1.date, p1.display_name, p1.email, p1.employee, p1.fax, p1.is_company, p1.lang, p1.mobile, p1.name, 
                    p1.parent_id, p1.phone, p1.state_id, p1.street, p1.street2, p1.supplier, p1.type, p1.tz, 
                    p1.use_parent_address, p1.user_id, p1.vat, p1.website, p1.zip,
                    c.id, c.code, c.name
                FROM res_partner p1
                    LEFT JOIN res_country c
                    ON c.id = p1.country_id
                WHERE p1.id > 4
                ORDER BY p1.id;
        """)
        
        openerp.tools.config.parse_config(cmdargs)
        dbname = openerp.tools.config['db_name']
        r = modules.registry.RegistryManager.get(dbname)
        cr = r.cursor()
        
        with api.Environment.manage():
            env = api.Environment(cr, 1, {})
            # Define target model 
            res_partner = env['res.partner']
            
            id_ptr = None
            c_data = {}
            while True:
                r = src_cr.fetchone()
                if not r:
                    self.process_item(res_partner, c_data)
                    break
                
                print r
                                
                company_id = 1
                country = env['res.country'].search([('code','=',r[31]),('name','=',r[32])])

                if id_ptr != r[0]:
                    self.process_item(res_partner, c_data)
                    id_ptr = r[0]

                    # Hack: lang
                    # Repair some custom languages duplicating es_ES
                    if not country or r[4] == 254:
                        country_id = 69
                    else:
                        country_id = country.id 

                    c_data = {
                        'id': r[0],
                        'active': r[1],
                        'company_id': r[2],
                        'city': r[3],
                        'country_id': country_id,
                        'create_date': r[5],
                        'create_uid': r[6],
                        'customer': r[7],
                        'date': r[8],
                        'display_name': r[9],
                        'email': r[10],
                        'employee': r[11],
                        'fax': r[12],
                        'is_company': r[13],
                        'lang': None,
                        'mobile': r[15],
                        'name': r[16],
                        'parent_id': None,
                        'phone': r[18],
                        'state_id': None,
                        'street': r[20],
                        'street2': r[21],
                        'supplier': r[22],
                        'type': r[23],
                        'tz': r[24],
                        'use_parent_address': r[25],
                        'user_id': None,
                        'vat': r[27],
                        'website': r[28],
                        'zip': r[29]
                    }
                
        cr.commit()
        cr.close()