(English version at bottom)

# Módulo para migrar de OpenERP 7 a Odoo 8
Este es un módulo que yo he desarrollado para migrar una base de datos en OpenERP 7 a Odoo 8. No es una herramienta de migración automatizada sino un conjunto de _scripts_ a ejecutar para tal fin.

## Instalación
Este módulo no requiere instalación. Sólo debe descargarse en el directorio de _addons_ del proyecto en Odoo 8.

## Cómo usarlo
Cada clase posee una consulta SQL para obtener la información del modelo a importar, conectándose a la base de datos anterior. Luego de obtener todos los datos asociados necesarios, se procede a asignarlos a su campo correspondiente en el modelo de la nueva versión. De este modo Odoo se encarga de ejecutar todos los procesos secundarios asociados al procesamiento de los datos y la generación de los datos complementarios en las demás tablas vinculadas.

Los códigos de migración se invocan por medio de un comando desde la cónsola mediante la siguiente sintaxis: 
/ruta-a/odoo/bin/odoo.py < comando > -c /ruta-a/openerp-server.conf

Ejecutar los comandos de migración en el siguiente orden:
1. importrespartnersuperadmin (actualiza los datos del superadministrador)
2. importrescompany (actualiza los datos de la compañía principal)
3. importaccountfiscalyear (importa los años fiscales creados)
4. importaccountperiod (importa los períodos fiscales registrados)
5. importrespartner (importa los clientes, proveedores y demás personas registradas)
6. importresusers (importa los usuarios registrados)
7. importproductcategory (importa las categorías a las que se asocian productos)
8. importproductproduct (importa los productos registrados y genera las plantillas de los mismos)
9. importsaleorder (importa las órdenes de ventas y presupuestos)
10. importsaleorderline (importa los productos asociados a las órdenes de ventas y presupuestos)
11. importaccountinvoice (importa las facturas y sus líneas de factura, generando el movimiento asociado y el número de factura, cuando corresponde)




# Module for migrate from OpenERP 7 to Odoo 8
It is a module I have developed to migrate an OpenERP 7 database to Odoo 8. It is not an automated tool for migrations but a series of migration scripts.

## Installation
This module doesn't need installation. You only have to download it to your Odoo 8 addons folder.

# How to use it
Each class have a SQL query to get module data in OpenERP 7 database. When it has all necessary attributes data, matches them to the respective fields in Odoo 8 module, executing on background all secondary actions associated to data processing, like an manual insertion through form views, generating complementary data in other associated tables.

Migration scripts are executed running the following command from console:
/path-to/odoo/bin/odoo.py < command > -c /path-to/openerp-server.conf

Available command in suggested order of execution:
1. importrespartnersuperadmin (update of superadmin data)
2. importrescompany (update of main company data)
3. importaccountfiscalyear (import fiscal years)
4. importaccountperiod (import periods in each fiscal year)
5. importrespartner (import customers, suppliers and other contacts)
6. importresusers (import registerd user accounts)
7. importproductcategory (import product categories)
8. importproductproduct (import product variants and generate product templates)
9. importsaleorder (import sale orders data only)
10. importsaleorderline (import lines in each sale order registered)
11. importaccountinovice (import invoices and their lines, creates associated move and generate invoice number when is necessary)
