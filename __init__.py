# -*- coding: utf-8 -*-
##############################################################################
#
#	Este módulo crea una extensión de la interfaz CLI. No es necesario instalarlo y basta con ejecutar un refresco de módulos.
#	
##############################################################################

from .cli import dentaltix_conn
from .cli import dx1_import_res_partner_superadmin
from .cli import dx2_import_res_company
from .cli import dx3_import_res_partner
from .cli import dx4_import_res_users
from .cli import dx5_import_product_category
from .cli import dx6_import_product_product
from .cli import dx7_import_account_fiscalyear
from .cli import dx8_import_account_period
# from .cli import dx9_import_sale_order
from .cli import import_sale_order
from .cli import import_sale_order_line
from .cli import dx10_import_account_invoice