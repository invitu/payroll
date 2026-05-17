# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    expense_in_payslip = fields.Boolean(
        string="Expenses reimbursed in payslip",
        default=True,
        help="Employee expenses to reimburse are added to the payslip. "
        "Employees inherit this setting; changing it here realigns "
        "all the company employees.",
    )

    def write(self, vals):
        res = super().write(vals)
        # Mecanique A: changing the company policy realigns every
        # employee of the company on the new value.
        if "expense_in_payslip" in vals:
            for company in self:
                employees = self.env["hr.employee"].search(
                    [("company_id", "=", company.id)]
                )
                employees.write({"expense_in_payslip": company.expense_in_payslip})
        return res
