# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    payslip_id = fields.Many2one(
        "hr.payslip",
        string="Payslip",
        readonly=True,
        copy=False,
        help="Payslip that reimburses this expense report.",
    )
