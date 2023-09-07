import xlsxwriter
from odoo import models
from datetime import datetime, timedelta

class InvoiceUtilidadXls(models.AbstractModel):
    _name = 'report.utilidades_pos.invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, obj):
        lines = []

        domain = [
            ('order_id.date_order', '>=', obj.fecha_ini),
            ('order_id.date_order', '<=', obj.fecha_fin),
        ]

        if obj.producto:
            domain.append(('product_id', '=', obj.producto.id))

        receipt_ids = self.env['pos.order.line'].search(domain)

        for line in receipt_ids:
            precio_venta_con_impuestos = line.price_unit * (1 + (line.tax_ids.amount / 100))
            costo = 0.0
            utilidadm = 0.0
            sale_price = line.price_unit * line.qty
            discount = (sale_price * line.discount) / 100
            costo = line.product_id.standard_price * line.qty
            utilidadm = (sale_price - discount) - costo
            vals = {
                'Producto': line.product_id.name,
                'Lote': line.order_id.pos_reference,
                'Fecha': line.order_id.date_order,
                'Cantidad': line.qty,
                'PrecioVenta': precio_venta_con_impuestos,
                'Costo': costo,
                'MontoUtilidad': utilidadm,
                'Categoria': line.product_id.categ_id.name,
            }
            lines.append(vals)

        return lines
    
    def generate_xlsx_report(self, workbook, data, wizard_obj):
        for obj in wizard_obj:
            lines = self.get_lines(obj)
            worksheet = workbook.add_worksheet('Reporte de utilidad')
            bold = workbook.add_format({'bold': True, 'align': 'center'})
            text = workbook.add_format({'font_size': 12, 'align': 'center'})

            worksheet.merge_range('A1:B1', 'Reporte de utilidad por producto', bold)
            worksheet.set_row(0, 30)  
            date_range = f'De {obj.fecha_ini.strftime("%d/%m/%Y")} a {obj.fecha_fin.strftime("%d/%m/%Y")}'
            worksheet.merge_range('A2:B2', date_range, text)
            worksheet.set_row(1, 20)

            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 2, 25)
            worksheet.set_column(3, 3, 25)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 5, 25)
            worksheet.set_column(6, 6, 25)
            worksheet.set_column(7, 7, 25)

            worksheet.write('A4', 'Producto', bold)
            worksheet.write('B4', 'Numero de recibo', bold)
            worksheet.write('C4', 'Fecha', bold)
            worksheet.write('D4', 'Cantidad', bold)
            worksheet.write('E4', 'Precio de venta', bold)
            worksheet.write('F4', 'Costo', bold)
            worksheet.write('G4', 'Monto de utilidad', bold)
            worksheet.write('H4', 'Categoria', bold)
            row = 4
            col = 0
            for res in lines:
                worksheet.write(row, col, res['Producto'], text)
                worksheet.write(row, col + 1, res['Lote'], text)
                #worksheet.write(row, col + 2, res['Fecha'], text)
                fecha = res['Fecha'].strftime('%d/%m/%Y')
                worksheet.write(row, col + 2, fecha, text)
                worksheet.write(row, col + 3, res['Cantidad'], text)
                worksheet.write(row, col + 4, str(self.env.user.company_id.currency_id.symbol) + str(res['PrecioVenta']), text)
                worksheet.write(row, col + 5, str(self.env.user.company_id.currency_id.symbol) + str(res['Costo']), text)
                worksheet.write(row, col + 6, str(self.env.user.company_id.currency_id.symbol) + str(res['MontoUtilidad']), text)
                worksheet.write(row, col + 7, res['Categoria'], text)
                row = row + 1