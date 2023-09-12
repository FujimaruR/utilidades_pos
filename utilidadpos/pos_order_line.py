from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_average_margin_percentage(self):
        sale_price = discount = cost = margin_amount = 0.0
        line_cost = line_margin_amount = margin_percentage = 0.0
        for record in self:
            if record.lines:
                for line in record.lines:
                    line.costo = line.product_id.standard_price * line.qty
                    costo = 0.0
                    sale_price = line.price_unit * line.qty
                    discount = (sale_price * line.discount) / 100
                    costo = line.product_id.standard_price * line.qty
                    line.margen = (sale_price - discount) - costo


    def action_pos_order_paid(self):
       for order in self:
          order._get_average_margin_percentage()
       res = super(PosOrder, self).action_pos_order_paid()
       return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    costo = fields.Float("Costo")
    margen = fields.Float("Margen")






