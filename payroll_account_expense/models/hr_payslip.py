# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _reconcile_expense_sheets(self):
        """Best-effort reconciliation between the unreconciled payable
        lines of the linked expense sheets and the matching lines of
        the payslip move.

        For an ``own_account`` expense sheet, the payable line is on the
        employee work contact payable account, with the work contact as
        partner. The payslip move line to match is the one the user
        mapped on the reimbursement rule (same account, same partner).

        Silent by design: if no matching line is found (e.g. the rule is
        not mapped to the expense payable account yet), nothing is
        reconciled and no error is raised. The accountant can always
        reconcile manually.
        """
        for payslip in self:
            move = payslip.move_id
            sheets = payslip.expense_sheet_ids
            if not move or not sheets:
                continue
            partner = payslip.employee_id.sudo().work_contact_id
            if not partner:
                continue
            sheet_lines = sheets.account_move_ids.line_ids.filtered(
                lambda line, p=partner: not line.reconciled
                and line.amount_residual
                and line.account_id.reconcile
                and line.partner_id == p
            )
            for account in sheet_lines.account_id:
                to_reconcile = sheet_lines.filtered(
                    lambda line, a=account: line.account_id == a
                )
                move_lines = move.line_ids.filtered(
                    lambda line, a=account, p=partner: line.account_id == a
                    and line.partner_id == p
                    and not line.reconciled
                )
                group = to_reconcile | move_lines
                if len(group) > 1:
                    try:
                        group.reconcile()
                    except Exception:
                        # Best-effort: never block payslip validation.
                        continue

    def action_payslip_done(self):
        res = super().action_payslip_done()
        self._reconcile_expense_sheets()
        return res
