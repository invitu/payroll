# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged

from odoo.addons.payroll.tests.common import TestPayslipBase


@tagged("post_install", "-at_install")
class TestPayrollAccountExpense(TestPayslipBase):
    def setUp(self):
        super().setUp()
        self.Payslip = self.env["hr.payslip"]

    def _make_payslip(self):
        return self.Payslip.create(
            {
                "employee_id": self.richard_emp.id,
                "contract_id": self.richard_contract.id,
                "struct_id": self.developer_pay_structure.id,
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
            }
        )

    def test_no_move_no_error(self):
        """Without a payslip move, reconciliation is a no-op."""
        payslip = self._make_payslip()
        # Method must not raise even when there is nothing to do.
        payslip._reconcile_expense_sheets()
        self.assertFalse(payslip.move_id)

    def test_no_sheets_no_error(self):
        """Without linked sheets, reconciliation is a no-op."""
        payslip = self._make_payslip()
        payslip._reconcile_expense_sheets()
        self.assertFalse(payslip.expense_sheet_ids)

    def test_done_calls_reconcile_without_error(self):
        """Validating a payslip with no expense data must not raise."""
        payslip = self._make_payslip()
        payslip.compute_sheet()
        payslip.action_payslip_done()
        self.assertEqual(payslip.state, "done")
