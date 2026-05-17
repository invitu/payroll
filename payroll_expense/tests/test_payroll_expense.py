# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged

from odoo.addons.payroll.tests.common import TestPayslipBase


@tagged("post_install", "-at_install")
class TestPayrollExpense(TestPayslipBase):
    def setUp(self):
        super().setUp()
        self.Sheet = self.env["hr.expense.sheet"]
        self.Expense = self.env["hr.expense"]
        self.product = self.env["product.product"].create(
            {"name": "Expense product", "can_be_expensed": True}
        )

    def _create_sheet(self, amount=100.0):
        expense = self.Expense.create(
            {
                "name": "Taxi",
                "employee_id": self.richard_emp.id,
                "product_id": self.product.id,
                "total_amount_currency": amount,
                "payment_mode": "own_account",
            }
        )
        sheet = self.Sheet.create(
            {
                "name": "Expense report",
                "employee_id": self.richard_emp.id,
                "expense_line_ids": [(6, 0, expense.ids)],
            }
        )
        return sheet

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

    # Company / employee opt-in
    def test_company_default_true(self):
        self.assertTrue(self.env.company.expense_in_payslip)

    def test_company_write_cascades_to_employees(self):
        self.richard_emp.expense_in_payslip = True
        self.env.company.expense_in_payslip = False
        self.assertFalse(self.richard_emp.expense_in_payslip)
        self.env.company.expense_in_payslip = True
        self.assertTrue(self.richard_emp.expense_in_payslip)

    def test_employee_override_kept_until_company_change(self):
        self.richard_emp.expense_in_payslip = False
        # company value unchanged -> override stays
        self.assertFalse(self.richard_emp.expense_in_payslip)

    # Work entry type data
    def test_work_entry_type_exists(self):
        wet = self.env.ref(
            "payroll_expense.work_entry_type_expense",
            raise_if_not_found=False,
        )
        self.assertTrue(wet)
        self.assertEqual(wet.code, "EXP_REIMB")

    # Eligibility selection
    def test_no_input_when_employee_opted_out(self):
        self.richard_emp.expense_in_payslip = False
        payslip = self._make_payslip()
        sheets = payslip._get_expense_sheets_to_reimburse()
        self.assertFalse(sheets)

    def test_link_and_unlink_idempotent(self):
        payslip = self._make_payslip()
        # No posted sheet yet -> nothing linked
        payslip._link_expense_sheets()
        self.assertFalse(payslip.expense_sheet_ids)

    # Lifecycle: cancel / draft unlink the sheets
    def test_cancel_unlinks_sheets(self):
        payslip = self._make_payslip()
        sheet = self._create_sheet()
        sheet.payslip_id = payslip.id
        payslip.action_payslip_cancel()
        self.assertFalse(sheet.payslip_id)

    def test_draft_unlinks_sheets(self):
        payslip = self._make_payslip()
        sheet = self._create_sheet()
        sheet.payslip_id = payslip.id
        payslip.action_payslip_draft()
        self.assertFalse(sheet.payslip_id)

    def test_expense_sheet_count(self):
        payslip = self._make_payslip()
        sheet = self._create_sheet()
        sheet.payslip_id = payslip.id
        payslip.invalidate_recordset()
        self.assertEqual(payslip.expense_sheet_count, 1)
