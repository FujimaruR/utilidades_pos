from odoo import fields, models, api
from datetime import datetime, timedelta

class XlsInvoiceUtilidad(models.Model):
    _name = "xls.invoice.utilidadpos"
    _description = "Invoice Utilidad Pos"

    fecha_ini = fields.Date(string='Fecha inicial', required=True)
    fecha_fin = fields.Date(string='Fecha final', required=True)
    producto = fields.Many2one('product.product', string='Producto')
    no_resultado = fields.Boolean(string='No Result', default=False)

    def print_xls_utilidadpos(self, context=None):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'xls.invoice.utilidadpos'
        datas['form'] = self.read()[0]
        return self.env.ref('utilidades_pos.utilidadpos_invoice_xls').report_action(self, data=datas)