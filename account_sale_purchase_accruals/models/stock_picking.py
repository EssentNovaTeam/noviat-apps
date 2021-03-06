# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models
from openerp.addons.account_sale_purchase_accruals.models.common_accrual \
    import CommonAccrual


class StockPicking(models.Model, CommonAccrual):
    _inherit = 'stock.picking'

    valuation_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='picking_id',
        string='Stock Valuation Journal Entries',
        readonly=True, copy=False)
    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order', compute='_compute_purchase_order_ids',
        string="Purchase Orders")

    @api.one
    def _compute_purchase_order_ids(self):
        stock_moves = self.move_lines
        po_lines = stock_moves.mapped('purchase_line_id')
        self.purchase_order_ids = po_lines.mapped('order_id')

    def _reconcile_invoice_accruals(self, pick_type):
        if pick_type == 'out':
            invoices = self.sale_id.invoice_ids
            inv_accruals = invoices.mapped('accrual_move_id')
            inv_amls = inv_accruals.mapped('line_id')
        else:
            invoices = self.purchase_order_ids.mapped('invoice_ids')
            inv_moves = invoices.mapped('move_id')
            inv_amls = inv_moves.mapped('line_id')
        if not invoices:
            return
        sp_amls = self.valuation_move_ids.mapped('line_id')

        accrual_lines = {}
        for sp_aml in sp_amls:
            product = sp_aml.product_id
            if pick_type == 'out':
                accrual_account = \
                    product.recursive_property_stock_account_output
            else:
                accrual_account = \
                    product.recursive_property_stock_account_input
            if accrual_account == sp_aml.account_id:
                accrual_lines[product.id] = sp_aml
                for inv_aml in inv_amls:
                    if inv_aml.account_id == accrual_account:
                        accrual_lines[product.id] += inv_aml
        if accrual_lines:
            self._reconcile_accrued_expense_lines(accrual_lines)

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if self.picking_type_id.code == 'outgoing':
            self._reconcile_invoice_accruals('out')
        elif self.picking_type_id.code == 'incoming':
            self._reconcile_invoice_accruals('in')
        return res
