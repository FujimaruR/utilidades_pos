import xlsxwriter
from odoo import models

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
            vals = {
                'Producto': line.product_id.name,
                'Lote': line.id,
                'Cantidad': line.qty,
                'UnidadDemedida': line.product_uom_id.name,
                'PrecioUnitario': line.price_unit,
                'Descuento': line.discount,
                'Impuestos': [(impuesto.name, impuesto.amount) for impuesto in line.tax_ids],
                'SubtotalnImpuestos': line.price_subtotal,
                'Subtotal': line.price_subtotal_incl,
            }
            lines.append(vals)

        return lines
    
    def generate_xlsx_report(self, workbook, data, wizard_obj):
        for obj in wizard_obj:
            lines = self.get_lines(obj)
            worksheet = workbook.add_worksheet('Reporte de utilidad')
            bold = workbook.add_format({'bold': True, 'align': 'center'})
            text = workbook.add_format({'font_size': 12, 'align': 'center'})

            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 2, 25)
            worksheet.set_column(3, 3, 25)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 5, 25)
            worksheet.set_column(6, 6, 25)
            worksheet.set_column(7, 7, 25)
            worksheet.set_column(8, 8, 25)

            worksheet.write('A1', 'Producto', bold)
            worksheet.write('B1', 'Lote', bold)
            worksheet.write('C1', 'Cantidad', bold)
            worksheet.write('D1', 'Unidad de medida', bold)
            worksheet.write('E1', 'Precio unitario', bold)
            worksheet.write('F1', 'Descuento', bold)
            worksheet.write('G1', 'Impuestos', bold)
            worksheet.write('H1', 'Subtotal sin impuestos', bold)
            worksheet.write('I1', 'Subtotal', bold)
            row = 1
            col = 0
            for res in lines:
                worksheet.write(row, col, res['Producto'], text)
                worksheet.write(row, col + 1, res['Lote'], text)
                worksheet.write(row, col + 2, res['Cantidad'], text)
                worksheet.write(row, col + 3, res['UnidadDemedida'], text)
                worksheet.write(row, col + 4, str(self.env.user.company_id.currency_id.symbol) + str(res['PrecioUnitario']), text)
                worksheet.write(row, col + 5, res['Descuento'], text)
                impuestos_str = ', '.join([f'{nombre}: {monto}' for nombre, monto in res['Impuestos']])
                worksheet.write(row, col + 6, impuestos_str, text)
                worksheet.write(row, col + 7, str(self.env.user.company_id.currency_id.symbol) + str(res['SubtotalnImpuestos']), text)
                worksheet.write(row, col + 8, str(self.env.user.company_id.currency_id.symbol) + str(res['Subtotal']), text)
                row = row + 1