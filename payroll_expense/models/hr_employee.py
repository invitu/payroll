# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    expense_in_payslip = fields.Boolean(
        string="Expenses reimbursed in payslip",
        default=lambda self: self.env.company.expense_in_payslip,
        groups="payroll.group_payroll_user",
        help="Expenses to reimburse for this employee are added to the "
        "payslip. Defaults to the company setting; can be overridden "
        "per employee (overrides are reset when the company setting "
        "changes).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "expense_in_payslip" not in vals:
                company = (
                    self.env["res.company"].browse(vals["company_id"])
                    if vals.get("company_id")
                    else self.env.company
                )
                vals["expense_in_payslip"] = company.expense_in_payslip
        return super().create(vals_list)
