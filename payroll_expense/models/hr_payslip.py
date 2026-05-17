# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    expense_sheet_ids = fields.One2many(
        "hr.expense.sheet",
        "payslip_id",
        string="Expense Reports",
        readonly=True,
    )
    expense_sheet_count = fields.Integer(
        compute="_compute_expense_sheet_count",
        string="Expense Reports Count",
    )

    def _compute_expense_sheet_count(self):
        for payslip in self:
            payslip.expense_sheet_count = len(payslip.expense_sheet_ids)

    def _get_expense_sheets_to_reimburse(self):
        """Expense sheets eligible to be reimbursed in this payslip.

        Criteria: paid by the employee, posted, not (fully) reimbursed,
        accounting date within the period, employee opted in, and not
        already linked to another active payslip.
        """
        self.ensure_one()
        if not self.employee_id or not self.employee_id.expense_in_payslip:
            return self.env["hr.expense.sheet"]
        return self.env["hr.expense.sheet"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("payment_mode", "=", "own_account"),
                ("state", "=", "post"),
                ("payment_state", "in", ("not_paid", "partial")),
                ("accounting_date", "<=", self.date_to),
                "|",
                ("payslip_id", "=", False),
                ("payslip_id.state", "=", "cancel"),
            ]
        )

    def _link_expense_sheets(self):
        """Idempotently (re)link eligible sheets to this payslip and
        unlink the ones no longer retained."""
        for payslip in self:
            eligible = payslip._get_expense_sheets_to_reimburse()
            current = payslip.expense_sheet_ids
            (current - eligible).write({"payslip_id": False})
            (eligible - current).write({"payslip_id": payslip.id})

    def get_inputs(self, contracts, date_from, date_to):
        res = super().get_inputs(contracts, date_from, date_to)
        work_entry_type = self.env.ref(
            "payroll_expense.work_entry_type_expense",
            raise_if_not_found=False,
        )
        code = work_entry_type.code if work_entry_type else "EXP_REIMB"
        for payslip in self:
            payslip._link_expense_sheets()
            sheets = payslip.expense_sheet_ids
            if not sheets:
                continue
            total = sum(sheets.mapped("amount_residual"))
            refs = ", ".join(sheets.mapped("name"))
            for contract in contracts:
                res.append(
                    {
                        "name": _("Expense reimbursement: %s", refs),
                        "code": code,
                        "amount": total,
                        "contract_id": contract.id,
                    }
                )
        return res

    def action_payslip_cancel(self):
        res = super().action_payslip_cancel()
        self.expense_sheet_ids.write({"payslip_id": False})
        return res

    def action_payslip_draft(self):
        res = super().action_payslip_draft()
        self.expense_sheet_ids.write({"payslip_id": False})
        return res

    def action_open_expense_sheets(self):
        self.ensure_one()
        return {
            "name": _("Expense Reports"),
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.sheet",
            "view_mode": "list,form",
            "domain": [("id", "in", self.expense_sheet_ids.ids)],
        }
