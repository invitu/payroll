# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    expense_in_payslip = fields.Boolean(
        related="company_id.expense_in_payslip",
        readonly=False,
        string="Expenses reimbursed in payslip",
        help="Employee expenses to reimburse are added to the payslip.",
    )
