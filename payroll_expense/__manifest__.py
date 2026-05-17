# Copyright 2026 INVITU (<https://www.invitu.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Payroll Expense",
    "version": "18.0.1.0.0",
    "category": "Payroll",
    "website": "https://github.com/OCA/payroll",
    "summary": "Reimburse employee expenses through the payslip.",
    "license": "LGPL-3",
    "author": "INVITU, Odoo Community Association (OCA)",
    "depends": ["payroll", "hr_expense"],
    "data": [
        "data/hr_work_entry_type_data.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_expense_sheet_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "demo": [
        "demo/hr_payroll_expense_demo.xml",
    ],
    "auto_install": True,
    "installable": True,
}
