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

from openerp import fields, models


class CodaAccountMappingRule(models.Model):
    _inherit = 'coda.account.mapping.rule'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product', index=True)
    reinvoice_key_id = fields.Many2one(
        comodel_name='account.reinvoice.key',
        string='Reinvoice Key', index=True)

    def _rule_select_extra(self, coda_bank_account_id):
        res = super(CodaAccountMappingRule, self)._rule_select_extra(
            coda_bank_account_id)
        return res + ', product_id, reinvoice_key_id'

    def _rule_result_extra(self, coda_bank_account_id):
        res = super(CodaAccountMappingRule, self)._rule_result_extra(
            coda_bank_account_id)
        return res + ['product_id', 'reinvoice_key_id']
