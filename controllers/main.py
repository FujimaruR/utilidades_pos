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
        fieldnames = ['Producto', 'Lote', 'Cantidad', 'Unidad de medida', 'Precio unitario', 'Descuento', 'Impuestos', 'Subtotal sin impuestos', 'Subtotal']
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_NONE, fieldnames=fieldnames)
        writer.writeheader()

        for inv in invoices:
            writer.writerow({'Producto': inv.product_id.name, 
                            'Lote': inv.id, 
                            'Cantidad': inv.qty, 
                            'Unidad de medida': inv.product_uom_id.name, #.encode('ascii', 'ignore') or '', 
                            'Precio unitario': inv.price_unit,
                            'Descuento': inv.discount, 
                            'Impuestos': [(impuesto.name, impuesto.amount) for impuesto in inv.tax_ids],
                            'SubtotalnImpuestos': inv.price_subtotal_incl,
                            'Subtotal': inv.price_subtotal,
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