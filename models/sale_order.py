from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    delivery_date = fields.Date()
    margin = fields.Float(compute="_compute_margin", store=True)

    @api.depends('order_line.product_template_id', 'order_line.product_template_id.standard_price', "order_line.product_uom_qty", "amount_total")
    def _compute_margin(self):
        for rec in self:
            rec.margin = rec.amount_total - sum(line.price_subtotal for line in rec.order_line)

    def action_request_approval(self):
        for rec in self:
            if rec.amount_total > 10000:
                rec.approval_state = 'pending'
            else:
                rec.approval_state = 'approved'

    def action_approve(self):
        for rec in self:
            rec.approval_state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.approval_state = 'rejected'

    def action_confirm(self):
        for rec in self:
            if rec.approval_state != 'approved':
                raise ValidationError("Only approved orders can be confirmed")

        return super().action_confirm()