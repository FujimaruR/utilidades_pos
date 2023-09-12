from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception
from odoo.http import content_disposition

from xlsxwriter.workbook import Workbook
import csv
import time
from datetime import datetime
from io import BytesIO

class BinaryFacturas(http.Controller):
    @http.route('/web/binary/download_xls', type='http', auth="public")
    @serialize_exception
    def download_xls(self,invoice_utilidad_id, **kw):
        invoice_utilidad = request.env['xls.invoice.utilidadpos'].sudo().browse(int(invoice_utilidad_id))
        invoice_ids = invoice_utilidad.invoice_ids.split('-')
        invoice_ids = [int(s) for s in invoice_ids]
        Model = request.env['pos.order.line']
        invoices = Model.browse(invoice_ids)
        timestamp = int(time.mktime(datetime.now().timetuple()))   
        csvfile = open('%s%s.csv' % ('/tmp/invoices_', timestamp), 'w')
        fieldnames = ['Producto', 'Lote', 'Fecha', 'Cantidad', 'PrecioVenta', 'Costo', 'MontoUtilidad', 'Categoria']
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_NONE, fieldnames=fieldnames)
        writer.writeheader()

        for inv in invoices:
            precio_venta_con_impuestos = inv.price_unit * (1 + (inv.tax_ids.amount / 100))
            costo = 0.0
            utilidadm = 0.0
            sale_price = inv.price_unit * inv.qty
            discount = (sale_price * inv.discount) / 100
            costo = inv.product_id.standard_price * inv.qty
            utilidadm = (sale_price - discount) - costo
            writer.writerow({'Producto': inv.product_id.name, 
                            'Numero de recibo': inv.order_id.pos_reference, 
                            'Fecha': inv.order_id.date_order, 
                            'Cantidad': inv.qty, #.encode('ascii', 'ignore') or '', 
                            'Precio de venta': precio_venta_con_impuestos,
                            'Costo': inv.costo, 
                            'Monto de utilidad': inv.margen,
                            'Categoria': inv.product_id.categ_id.name,
                            })


        csvfile.close()   
        output = BytesIO() #StringIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True, 'border':   1,})
        border = workbook.add_format({'border':   1,})
        with open('%s%s.csv' % ('/tmp/invoices_', timestamp), 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    #print (r, c, col)
                    if r == 0:
                        worksheet.write(r, c, col, bold)
                    else:
                        worksheet.write(r, c, col, border)
                        # worksheet.set_column(c, c, len(col),formater)
        workbook.close()
        output.seek(0)	 
        binary = output.read()
            
        #res = Model.to_xml(cr, uid, context=context)
        if not binary:
            #print 'no binary'
            return request.not_found()
        else:
            filename = '%s%s.xls' % ('invoices_', timestamp)
            return request.make_response(binary,
                               [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                ('Pragma', 'public'), 
                                ('Expires', '0'),
                                ('Cache-Control', 'must-revalidate, post-check=0, pre-check=0'),
                                ('Cache-Control', 'private'),
                                ('Content-Length', len(binary)),
                                ('Content-Transfer-Encoding', 'binary'),
                                ('Content-Disposition', content_disposition(filename))])